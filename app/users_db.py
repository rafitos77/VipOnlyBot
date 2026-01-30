
"""
User management module with Database support - v8.2
Handles user data, licenses, credits, and referral system
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT,
                    is_vip INTEGER DEFAULT 0,
                    license_type TEXT,
                    license_expiry DATETIME,
                    credits INTEGER DEFAULT 0,
                    daily_previews_used INTEGER DEFAULT 0,
                    last_preview_date DATE,
                    is_god_mode INTEGER DEFAULT 0,
                    referred_by INTEGER,
                    referral_count INTEGER DEFAULT 0,
                    first_seen DATETIME,
                    last_seen DATETIME
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    transaction_id TEXT,
                    gateway TEXT,
                    status_detail TEXT,
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
            # Admin starts with GOD mode OFF to allow testing as normal user
            is_god = 0
            cursor.execute('''
                INSERT INTO users (user_id, is_god_mode, first_seen, last_seen)
                VALUES (?, ?, ?, ?)
            ''', (user_id, is_god, now, now))
            conn.commit()
            
            return self.get_user(user_id)

    def update_user(self, user_id: int, **kwargs):
        """Update user fields"""
        if not kwargs:
            return
        
        # Convert values for SQLite
        for k, v in kwargs.items():
            if isinstance(v, bool):
                kwargs[k] = 1 if v else 0
        
        # Use parameterized query to prevent SQL injection
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        
        with self._get_conn() as conn:
            bindings = values + [datetime.now().isoformat(), user_id]
            # Field names are from kwargs keys (internal code), but still use parameterized query
            conn.execute(f"UPDATE users SET {fields}, last_seen = ? WHERE user_id = ?", 
                        bindings)
            conn.commit()

    def check_preview_limit(self, user_id: int) -> bool:
        """Check if user can still use free previews today"""
        user = self.get_user(user_id)
        
        if self.is_license_active(user_id):
            return True
            
        today = datetime.now().date().isoformat()
        last_date = user.get('last_preview_date')
        used = int(user.get('daily_previews_used', 0))
        
        if last_date != today:
            self.update_user(user_id, daily_previews_used=0, last_preview_date=today)
            return True
            
        return used < 3

    def increment_previews(self, user_id: int):
        """Increment daily preview count"""
        user = self.get_user(user_id)
        used = int(user.get('daily_previews_used', 0))
        self.update_user(user_id, daily_previews_used=used + 1)

    def use_credit(self, user_id: int) -> bool:
        """Use one credit for full media access"""
        user = self.get_user(user_id)
        credits = int(user.get('credits', 0))
        if credits > 0:
            self.update_user(user_id, credits=credits - 1)
            return True
        return False

    def process_referral(self, new_user_id: int, referrer_id: int):
        """Handle new user referred by someone"""
        if new_user_id == referrer_id:
            return
            
        referrer = self.get_user(referrer_id)
        if not referrer:
            return
            
        new_user = self.get_user(new_user_id)
        if not new_user.get('referred_by'):
            self.update_user(new_user_id, referred_by=referrer_id)
            
            current_count = int(referrer.get('referral_count', 0))
            current_credits = int(referrer.get('credits', 0))
            self.update_user(referrer_id, 
                             referral_count=current_count + 1,
                             credits=current_credits + 3)
            logger.info(f"User {referrer_id} rewarded for referring {new_user_id}")

    def activate_license(self, user_id: int, plan_type: str):
        """Activate a license for a user (idempotent - safe to call multiple times)"""
        # Validate plan_type
        valid_plans = ['weekly', 'monthly', 'lifetime']
        if plan_type not in valid_plans:
            logger.error(f"Invalid plan_type: {plan_type}. Must be one of {valid_plans}")
            return
        
        now = datetime.now()
        expiry = None
        
        if plan_type == 'weekly':
            expiry = (now + timedelta(days=7)).isoformat()
        elif plan_type == 'monthly':
            expiry = (now + timedelta(days=30)).isoformat()
        elif plan_type == 'lifetime':
            expiry = None
        
        # Get current license to check if upgrade/downgrade
        current_user = self.get_user(user_id)
        current_expiry = current_user.get('license_expiry')
        current_type = current_user.get('license_type')
        
        # If user already has lifetime, don't downgrade
        if current_type == 'lifetime' and plan_type != 'lifetime':
            logger.info(f"User {user_id} already has lifetime license, skipping activation of {plan_type}")
            return
        
        # If user has active license and new one is not lifetime, extend if same type or upgrade
        if current_expiry and current_type:
            try:
                current_expiry_dt = datetime.fromisoformat(current_expiry)
                if current_expiry_dt > now:
                    # Active license exists
                    if current_type == plan_type:
                        # Same plan - extend from current expiry
                        if plan_type == 'weekly':
                            expiry = (current_expiry_dt + timedelta(days=7)).isoformat()
                        elif plan_type == 'monthly':
                            expiry = (current_expiry_dt + timedelta(days=30)).isoformat()
                        logger.info(f"Extending {plan_type} license for user {user_id}")
                    elif plan_type == 'lifetime':
                        # Upgrade to lifetime
                        expiry = None
                        logger.info(f"Upgrading user {user_id} to lifetime license")
                    else:
                        # Different plan - start from now
                        logger.info(f"Changing license type for user {user_id} from {current_type} to {plan_type}")
            except (ValueError, TypeError):
                # Invalid expiry format, start fresh
                pass
            
        self.update_user(
            user_id, 
            is_vip=1, 
            license_type=plan_type, 
            license_expiry=expiry
        )
        logger.info(f"License {plan_type} activated for user {user_id}")

    def add_transaction(self, user_id: int, transaction_id: str, gateway: str, amount: float, currency: str, plan_type: str, status: str, status_detail: Optional[str] = None):
        """Add a new transaction to the database (idempotent - won't duplicate)"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Check if transaction already exists
            cursor.execute("SELECT id FROM transactions WHERE transaction_id = ?", (transaction_id,))
            existing = cursor.fetchone()
            
            if existing:
                logger.warning(f"Transaction {transaction_id} already exists, skipping duplicate")
                return
            
            cursor.execute('''
                INSERT INTO transactions (user_id, transaction_id, gateway, amount, currency, plan_type, status, status_detail, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, transaction_id, gateway, amount, currency, plan_type, status, status_detail, datetime.now().isoformat()))
            conn.commit()
        logger.info(f"Transaction {transaction_id} recorded for user {user_id} via {gateway}")

    def update_transaction_status(self, transaction_id: str, status: str, status_detail: Optional[str] = None):
        """Update the status of an existing transaction"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if status_detail:
                cursor.execute("UPDATE transactions SET status = ?, status_detail = ? WHERE transaction_id = ?", (status, status_detail, transaction_id))
            else:
                cursor.execute("UPDATE transactions SET status = ? WHERE transaction_id = ?", (status, transaction_id))
            conn.commit()
        logger.info(f"Transaction {transaction_id} status updated to {status}")

    def is_license_active(self, user_id: int) -> bool:
        """Check if user has an active license or credits"""
        user = self.get_user(user_id)
        
        # Admin logic: GOD mode overrides EVERYTHING
        if user_id == config.ADMIN_ID:
            # Explicitly check for integer 1
            if int(user.get('is_god_mode', 0)) == 1:
                return True
            
        if int(user.get('credits', 0)) > 0:
            return True
            
        if int(user.get('is_vip', 0)) != 1:
            return False
            
        expiry_str = user.get('license_expiry')
        if not expiry_str:
            return True
            
        expiry = datetime.fromisoformat(expiry_str)
        if expiry > datetime.now():
            return True
            
        self.update_user(user_id, is_vip=0, license_type=None, license_expiry=None)
        return False

    def get_pricing(self, lang: str) -> Dict[str, Dict[str, Any]]:
        """Get regional pricing based on language/region"""
        pricing = {
            'en': {
                'weekly': {'price': 5.00, 'currency': 'USD', 'label': '$5.00'},
                'monthly': {'price': 14.00, 'currency': 'USD', 'label': '$14.00'},
                'lifetime': {'price': 25.00, 'currency': 'USD', 'label': '$25.00'}
            },
            'pt': {
                'weekly': {'price': 9.90, 'currency': 'BRL', 'label': 'R$ 9,90'},
                'monthly': {'price': 29.90, 'currency': 'BRL', 'label': 'R$ 29,90'},
                'lifetime': {'price': 59.90, 'currency': 'BRL', 'label': 'R$ 59,90'}
            },
            'es': {
                'weekly': {'price': 1.99, 'currency': 'USD', 'label': '$1.99'},
                'monthly': {'price': 5.99, 'currency': 'USD', 'label': '$5.99'},
                'lifetime': {'price': 12.99, 'currency': 'USD', 'label': '$12.99'}
            }
        }
        return pricing.get(lang, pricing['en'])

# Global instance
user_db = UserDB()
