# agents/memory_bank.py
import sqlite3
import json
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger("memory_bank")

DB_FILE = "agents_memory.db"
if os.environ.get('K_SERVICE'):
    DB_FILE = "/tmp/agents_memory.db"

USE_CLOUD_SQL = os.getenv("USE_CLOUD_SQL", "False") == "True"

class MemoryBank:
    def __init__(self, path=DB_FILE):
        self.use_cloud = USE_CLOUD_SQL
        if self.use_cloud:
            logger.info("Connecting to Cloud SQL...")
            # In production, use SQLAlchemy or cloud-sql-python-connector
            # self.conn = connect_to_cloud_sql()
            pass
        else:
            self.conn = sqlite3.connect(path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self._init_tables()

    def _init_tables(self):
        if self.use_cloud: return # Assume schema managed by migration
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS customers (phone TEXT PRIMARY KEY, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS fabric_kb (fabric_key TEXT PRIMARY KEY, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS redeem_codes (code TEXT PRIMARY KEY, phone TEXT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, phone TEXT, status TEXT, data TEXT, timestamp REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS feedback (id TEXT PRIMARY KEY, order_id TEXT, rating INTEGER, comment TEXT, timestamp REAL)")
        self.conn.commit()

    def save_customer(self, phone: str, profile: Dict):
        if self.use_cloud:
            logger.info(f"Cloud Save Customer: {phone}")
            return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO customers (phone, data) VALUES (?, ?)", (phone, json.dumps(profile)))
        self.conn.commit()

    def get_customer(self, phone: str) -> Optional[Dict]:
        if self.use_cloud: return None
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM customers WHERE phone = ?", (phone,))
        r = cur.fetchone()
        return json.loads(r[0]) if r else None

    def get_all_customers(self) -> list:
        if self.use_cloud: return []
        cur = self.conn.cursor()
        cur.execute("SELECT phone, data FROM customers")
        rows = cur.fetchall()
        results = []
        for r in rows:
            d = json.loads(r[1])
            d['phone'] = r[0]
            results.append(d)
        return results

    def save_fabric(self, key: str, data: Dict):
        if self.use_cloud: return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO fabric_kb (fabric_key, data) VALUES (?, ?)", (key, json.dumps(data)))
        self.conn.commit()

    def get_fabric(self, key: str) -> Optional[Dict]:
        if self.use_cloud: return None
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM fabric_kb WHERE fabric_key = ?", (key,))
        r = cur.fetchone()
        return json.loads(r[0]) if r else None

    def save_redeem(self, code: str, phone: str, data: Dict):
        if self.use_cloud: return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO redeem_codes (code, phone, data) VALUES (?, ?, ?)", (code, phone, json.dumps(data)))
        self.conn.commit()

    def get_redeem(self, code: str) -> Optional[Dict]:
        if self.use_cloud: return None
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM redeem_codes WHERE code = ?", (code,))
        r = cur.fetchone()
        return json.loads(r[0]) if r else None

    def get_redeems_by_phone(self, phone: str) -> list:
        if self.use_cloud: return []
        cur = self.conn.cursor()
        cur.execute("SELECT code, data FROM redeem_codes WHERE phone = ?", (phone,))
        rows = cur.fetchall()
        results = []
        for r in rows:
            d = json.loads(r[1])
            d['code'] = r[0]
            results.append(d)
        return results

    def get_all_redeems(self) -> list:
        if self.use_cloud: return []
        cur = self.conn.cursor()
        # Limit to last 100 generated codes to prevent UI freeze
        cur.execute("SELECT code, phone, data FROM redeem_codes ORDER BY rowid DESC LIMIT 100")
        rows = cur.fetchall()
        results = []
        for r in rows:
            d = json.loads(r[2])
            d['code'] = r[0]
            d['phone'] = r[1]
            results.append(d)
        return results

    def save_order(self, order_id: str, phone: str, status: str, data: Dict):
        if self.use_cloud: return
        import time
        ts = data.get('timestamp', time.time())
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO orders (id, phone, status, data, timestamp) VALUES (?, ?, ?, ?, ?)", 
                   (order_id, phone, status, json.dumps(data), ts))
        self.conn.commit()

    def get_orders_by_phone(self, phone: str) -> list:
        if self.use_cloud: return []
        cur = self.conn.cursor()
        cur.execute("SELECT id, status, data, timestamp FROM orders WHERE phone = ? ORDER BY timestamp DESC", (phone,))
        rows = cur.fetchall()
        results = []
        for r in rows:
            d = json.loads(r[2])
            d['id'] = r[0]
            d['status'] = r[1]
            d['timestamp'] = r[3]
            results.append(d)
        return results

    def get_all_orders(self) -> list:
        if self.use_cloud: return []
        cur = self.conn.cursor()
        cur.execute("SELECT id, phone, status, data, timestamp FROM orders ORDER BY timestamp DESC LIMIT 100")
        rows = cur.fetchall()
        results = []
        for r in rows:
            d = json.loads(r[3])
            d['id'] = r[0]
            d['phone'] = r[1]
            d['status'] = r[2]
            d['timestamp'] = r[4]
            results.append(d)
        return results

    def update_order_status(self, order_id: str, status: str):
        if self.use_cloud: return
        cur = self.conn.cursor()
        cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        self.conn.commit()

    def save_feedback(self, feedback_id: str, order_id: str, rating: int, comment: str):
        if self.use_cloud: return
        import time
        cur = self.conn.cursor()
        cur.execute("INSERT INTO feedback (id, order_id, rating, comment, timestamp) VALUES (?, ?, ?, ?, ?)", 
                   (feedback_id, order_id, rating, comment, time.time()))
        self.conn.commit()

    def get_all_feedback(self) -> list:
        if self.use_cloud: return []
        cur = self.conn.cursor()
        cur.execute("SELECT id, order_id, rating, comment, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 100")
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0], "order_id": r[1], "rating": r[2], "comment": r[3], "timestamp": r[4]
            })
        return results
