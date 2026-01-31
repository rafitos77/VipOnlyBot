
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
                    paypal_order_id TEXT,
                    amount REAL,
                    currency TEXT,
                    plan_type TEXT,
                    status TEXT,
                    created_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # New unified payments table (Stripe / PushinPay / etc.)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL UNIQUE,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    plan_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    paid_at DATETIME,
                    raw_payload TEXT,
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
            # Admin GOD mode default can be set via ADMIN_GOD_MODE env (Railway Variables)
            is_god = 1 if (user_id == config.ADMIN_ID and str(os.getenv('ADMIN_GOD_MODE','0')).lower() in ('1','true','yes','on')) else 0
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

        # Ensure the user row exists (important when update_user() is called
        # before any get_user() call, e.g. activating a license for a fresh ID).
        self.get_user(user_id)
        
        # Convert values for SQLite
        for k, v in kwargs.items():
            if isinstance(v, bool):
                kwargs[k] = 1 if v else 0
        
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values())
        
        with self._get_conn() as conn:
            bindings = values + [datetime.now().isoformat(), user_id]
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


    # -------------------------
    # Payments (Stripe/PushinPay)
    # -------------------------
    def create_pending_payment(
        self,
        *,
        user_id: int,
        provider: str,
        external_id: str,
        amount: float,
        currency: str,
        plan_type: str,
        raw_payload: str = None,
    ):
        """Persist a pending payment so a webhook can later map it to a user."""
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO payments
                    (user_id, provider, external_id, amount, currency, plan_type, status, created_at, raw_payload)
                VALUES
                    (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
                """,
                (user_id, provider, external_id, amount, currency, plan_type, now, raw_payload),
            )
            conn.commit()

    def get_payment_by_external_id(self, provider: str, external_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM payments WHERE provider = ? AND external_id = ? ORDER BY id DESC LIMIT 1",
                (provider, external_id),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def mark_payment_paid(self, provider: str, external_id: str, raw_payload: str = None):
        """Mark payment as paid, idempotent."""
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE payments
                SET status = 'paid', paid_at = COALESCE(paid_at, ?), raw_payload = COALESCE(raw_payload, ?)
                WHERE provider = ? AND external_id = ?
                """,
                (now, raw_payload, provider, external_id),
            )
            conn.commit()

    def is_payment_already_paid(self, provider: str, external_id: str) -> bool:
        p = self.get_payment_by_external_id(provider, external_id)
        return bool(p and p.get('status') == 'paid')
    def activate_license(self, user_id: int, plan_type: str):
        """Activate a license for a user"""
        now = datetime.now()
        expiry = None
        
        if plan_type == 'weekly':
            expiry = (now + timedelta(days=7)).isoformat()
        elif plan_type == 'monthly':
            expiry = (now + timedelta(days=30)).isoformat()
        elif plan_type == 'lifetime':
            expiry = None
            
        self.update_user(
            user_id, 
            is_vip=1, 
            license_type=plan_type, 
            license_expiry=expiry
        )
        logger.info(f"License {plan_type} activated for user {user_id}")

    def is_license_active(self, user_id: int) -> bool:
        """Check if user has an active license or credits"""
        user = self.get_user(user_id)
        
        # Admin logic: GOD mode is a TEST toggle for the admin.
        # - If ADMIN_FORCE_VIP=1, admin is always VIP (cannot be disabled).
        # - Otherwise, admin VIP depends on the DB toggle (⚡ MODO GOD), so you can
        #   turn it ON/OFF to see the normal user experience.
        if user_id == config.ADMIN_ID:
            if str(os.getenv('ADMIN_FORCE_VIP','0')).lower() in ('1','true','yes','on'):
                return True
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