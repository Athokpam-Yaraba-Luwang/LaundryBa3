# agents/memory_bank.py
import sqlite3
import json
import os
import logging
from typing import Optional, Dict
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

logger = logging.getLogger("memory_bank")

DB_FILE = "agents_memory.db"
if os.environ.get('K_SERVICE'):
    DB_FILE = "/tmp/agents_memory.db"

USE_CLOUD_SQL = os.getenv("USE_CLOUD_SQL", "False") == "True"

class MemoryBank:
    def __init__(self, path=DB_FILE):
        self.use_cloud = Config.USE_FIRESTORE
        if self.use_cloud:
            logger.info("Connecting to Google Firestore...")
            try:
                from google.cloud import firestore
                self.db = firestore.Client()
                logger.info("Firestore connected.")
            except Exception as e:
                logger.error(f"Failed to connect to Firestore: {e}")
                # Fallback to SQLite if Firestore fails (e.g. local without creds)
                self.use_cloud = False
        
        if not self.use_cloud:
            self.conn = sqlite3.connect(path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self._init_tables()

    def _init_tables(self):
        if self.use_cloud: return
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS customers (phone TEXT PRIMARY KEY, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS fabric_kb (fabric_key TEXT PRIMARY KEY, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS redeem_codes (code TEXT PRIMARY KEY, phone TEXT, data TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, phone TEXT, status TEXT, data TEXT, timestamp REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS feedback (id TEXT PRIMARY KEY, order_id TEXT, rating INTEGER, comment TEXT, timestamp REAL)")
        self.conn.commit()

    def save_customer(self, phone: str, profile: Dict):
        if self.use_cloud:
            self.db.collection('customers').document(phone).set(profile)
            return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO customers (phone, data) VALUES (?, ?)", (phone, json.dumps(profile)))
        self.conn.commit()

    def get_customer(self, phone: str) -> Optional[Dict]:
        if self.use_cloud:
            doc = self.db.collection('customers').document(phone).get()
            return doc.to_dict() if doc.exists else None
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM customers WHERE phone = ?", (phone,))
        r = cur.fetchone()
        return json.loads(r[0]) if r else None

    def get_all_customers(self) -> list:
        if self.use_cloud:
            docs = self.db.collection('customers').stream()
            return [{"phone": d.id, **d.to_dict()} for d in docs]
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
        if self.use_cloud:
            self.db.collection('fabric_kb').document(key).set(data)
            return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO fabric_kb (fabric_key, data) VALUES (?, ?)", (key, json.dumps(data)))
        self.conn.commit()

    def get_fabric(self, key: str) -> Optional[Dict]:
        if self.use_cloud:
            doc = self.db.collection('fabric_kb').document(key).get()
            return doc.to_dict() if doc.exists else None
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM fabric_kb WHERE fabric_key = ?", (key,))
        r = cur.fetchone()
        return json.loads(r[0]) if r else None

    def save_redeem(self, code: str, phone: str, data: Dict):
        if self.use_cloud:
            data['phone'] = phone # Ensure phone is in data for Firestore
            self.db.collection('redeem_codes').document(code).set(data)
            return
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO redeem_codes (code, phone, data) VALUES (?, ?, ?)", (code, phone, json.dumps(data)))
        self.conn.commit()

    def get_redeem(self, code: str) -> Optional[Dict]:
        if self.use_cloud:
            doc = self.db.collection('redeem_codes').document(code).get()
            return doc.to_dict() if doc.exists else None
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM redeem_codes WHERE code = ?", (code,))
        r = cur.fetchone()
        return json.loads(r[0]) if r else None

    def get_redeems_by_phone(self, phone: str) -> list:
        if self.use_cloud:
            docs = self.db.collection('redeem_codes').where('phone', '==', phone).stream()
            return [{"code": d.id, **d.to_dict()} for d in docs]
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
        if self.use_cloud:
            docs = self.db.collection('redeem_codes').limit(100).stream()
            return [{"code": d.id, **d.to_dict()} for d in docs]
        cur = self.conn.cursor()
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
        if self.use_cloud:
            import time
            ts = data.get('timestamp', time.time())
            doc_data = {
                "phone": phone,
                "status": status,
                "timestamp": ts,
                "data": data # Store full blob to match SQLite structure or flatten
            }
            # Flatten for easier querying if needed, but keeping structure similar to SQLite for now
            self.db.collection('orders').document(order_id).set(doc_data)
            return
        import time
        ts = data.get('timestamp', time.time())
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO orders (id, phone, status, data, timestamp) VALUES (?, ?, ?, ?, ?)", 
                   (order_id, phone, status, json.dumps(data), ts))
        self.conn.commit()

    def get_orders_by_phone(self, phone: str) -> list:
        if self.use_cloud:
            from google.cloud import firestore
            # Remove order_by to avoid needing a composite index immediately
            docs = self.db.collection('orders').where('phone', '==', phone).stream()
            results = []
            for d in docs:
                dd = d.to_dict()
                # Reconstruct format expected by app
                order_data = dd.get('data', {})
                order_data['id'] = d.id
                order_data['status'] = dd.get('status')
                order_data['timestamp'] = dd.get('timestamp')
                results.append(order_data)
            # Sort in Python
            results.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return results
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
        if self.use_cloud:
            from google.cloud import firestore
            docs = self.db.collection('orders').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(100).stream()
            results = []
            for d in docs:
                dd = d.to_dict()
                order_data = dd.get('data', {})
                order_data['id'] = d.id
                order_data['phone'] = dd.get('phone')
                order_data['status'] = dd.get('status')
                order_data['timestamp'] = dd.get('timestamp')
                results.append(order_data)
            return results
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
        if self.use_cloud:
            self.db.collection('orders').document(order_id).update({"status": status})
            return
        cur = self.conn.cursor()
        cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        self.conn.commit()

    def save_feedback(self, feedback_id: str, order_id: str, rating: int, comment: str):
        if self.use_cloud:
            import time
            self.db.collection('feedback').document(feedback_id).set({
                "order_id": order_id,
                "rating": rating,
                "comment": comment,
                "timestamp": time.time()
            })
            return
        import time
        cur = self.conn.cursor()
        cur.execute("INSERT INTO feedback (id, order_id, rating, comment, timestamp) VALUES (?, ?, ?, ?, ?)", 
                   (feedback_id, order_id, rating, comment, time.time()))
        self.conn.commit()

    def get_all_feedback(self) -> list:
        if self.use_cloud:
            from google.cloud import firestore
            docs = self.db.collection('feedback').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(100).stream()
            return [{"id": d.id, **d.to_dict()} for d in docs]
        cur = self.conn.cursor()
        cur.execute("SELECT id, order_id, rating, comment, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 100")
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0], "order_id": r[1], "rating": r[2], "comment": r[3], "timestamp": r[4]
            })
        return results
