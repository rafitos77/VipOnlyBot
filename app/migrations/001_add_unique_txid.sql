-- Migration: Add unique index on transactions.transaction_id to enforce idempotency
-- Run this once against the SQLite DB (e.g., sqlite3 /data/bot_data.db < 001_add_unique_txid.sql)
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;
CREATE UNIQUE INDEX IF NOT EXISTS idx_transactions_txid ON transactions(transaction_id);
COMMIT;

