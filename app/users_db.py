"""
User management module with Database support
Handles user data, licenses, credits, and regional pricing
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.config import Config
config = Config()

logger = logging.getLogger(__name__)

class UserDB:
    """Manages user data and licenses using SQLite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Ordem de prioridade para o banco de dados:
            # 1. Variável de ambiente DATABASE_URL (se fosse Postgres, mas aqui é SQLite)
            # 2. Caminho fixo para volume no Railway (/data)
            # 3. Diretório atual
            if os.path.exists("/data"):
                self.db_path = "/data/bot_data.db"
            elif os.getenv("RAILWAY_VOLUME_MOUNT_PATH"):
                self.db_path = os.path.join(os.getenv("RAILWAY_VOLUME_MOUNT_PATH"), "bot_data.db")
            else:
                self.db_path = "bot_data.db"
        else:
            self.db_path = db_path
            
        logger.info(f"Using database at: {self.db_path}")
        self._init_db()
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Initialize database tables"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'pt',
                    is_vip BOOLEAN DEFAULT 0,
                    license_type TEXT, -- 'weekly', 'monthly', 'lifetime'
                    license_expiry DATETIME,
                    credits INTEGER DEFAULT 0,
                    daily_previews_used INTEGER DEFAULT 0,
                    last_preview_date DATE,
                    first_seen DATETIME,
                    last_seen DATETIME
                )
            ''')
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    paypal_order_id TEXT,
                    amount REAL,
                    currency TEXT,
                    plan_type TEXT,
                    status TEXT,
                    created_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            conn.commit()

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user data, create if doesn't exist"""
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            
            # Create new user
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (user_id, first_seen, last_seen)
                VALUES (?, ?, ?)
            ''', (user_id, now, now))
            conn.commit()
            
            return self.get_user(user_id)

    def update_user(self, user_id: int, **kwargs):
        """Update user fields"""
        if not kwargs:
            return
        
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        
        with self._get_conn() as conn:
            # Bindings: [kwargs_values..., last_seen_value, user_id]
            bindings = values + [datetime.now().isoformat(), user_id]
            conn.execute(f"UPDATE users SET {fields}, last_seen = ? WHERE user_id = ?", 
                        bindings)
            conn.commit()

    def check_preview_limit(self, user_id: int) -> bool:
        """Check if user can still use free previews today"""
        user = self.get_user(user_id)
        
        # Admins and VIPs have no limit
        if user_id == config.ADMIN_ID or user.get('is_vip') or user.get('license_type'):
            return True
            
        today = datetime.now().date().isoformat()
        last_date = user.get('last_preview_date')
        used = user.get('daily_previews_used', 0)
        
        if last_date != today:
            # Reset for new day
            self.update_user(user_id, daily_previews_used=0, last_preview_date=today)
            return True
            
        return used < 3

    def increment_previews(self, user_id: int):
        """Increment daily preview count"""
        user = self.get_user(user_id)
        used = user.get('daily_previews_used', 0)
        self.update_user(user_id, daily_previews_used=used + 1)

    def activate_license(self, user_id: int, plan_type: str):
        """Activate a license for a user"""
        now = datetime.now()
        expiry = None
        
        if plan_type == 'weekly':
            expiry = (now + timedelta(days=7)).isoformat()
        elif plan_type == 'monthly':
            expiry = (now + timedelta(days=30)).isoformat()
        elif plan_type == 'lifetime':
            expiry = None # No expiry
            
        self.update_user(
            user_id, 
            is_vip=True, 
            license_type=plan_type, 
            license_expiry=expiry
        )
        logger.info(f"License {plan_type} activated for user {user_id}")

    def is_license_active(self, user_id: int) -> bool:
        """Check if user has an active license"""
        user = self.get_user(user_id)
        if user_id == config.ADMIN_ID:
            return True
            
        if not user.get('is_vip'):
            return False
            
        expiry_str = user.get('license_expiry')
        if not expiry_str: # Lifetime
            return True
            
        expiry = datetime.fromisoformat(expiry_str)
        if expiry > datetime.now():
            return True
            
        # License expired
        self.update_user(user_id, is_vip=False, license_type=None, license_expiry=None)
        return False

    def get_pricing(self, lang: str) -> Dict[str, Dict[str, Any]]:
        """Get regional pricing based on language/region"""
        # Base prices in USD
        pricing = {
            'en': {
                'weekly': {'price': 5.00, 'currency': 'USD', 'label': '$5.00'},
                'monthly': {'price': 14.00, 'currency': 'USD', 'label': '$14.00'},
                'lifetime': {'price': 25.00, 'currency': 'USD', 'label': '$25.00'}
            },
            'pt': { # Brazil - Preços mais acessíveis
                'weekly': {'price': 9.90, 'currency': 'BRL', 'label': 'R$ 9,90'},
                'monthly': {'price': 29.90, 'currency': 'BRL', 'label': 'R$ 29,90'},
                'lifetime': {'price': 59.90, 'currency': 'BRL', 'label': 'R$ 59,90'}
            },
            'es': { # LATAM - Preços mais acessíveis
                'weekly': {'price': 1.99, 'currency': 'USD', 'label': '$1.99'},
                'monthly': {'price': 5.99, 'currency': 'USD', 'label': '$5.99'},
                'lifetime': {'price': 12.99, 'currency': 'USD', 'label': '$12.99'}
            }
        }
        return pricing.get(lang, pricing['en'])

# Global instance
user_db = UserDB()
