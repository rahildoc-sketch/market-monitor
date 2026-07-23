import sqlite3
from models import Announcement

DB_FILE = "announcements.db"

def init_db():
    """Creates the SQLite database and table if they do not exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                seq TEXT PRIMARY KEY,
                exchange TEXT,
                time TEXT,
                symbol TEXT,
                company TEXT,
                type TEXT,
                pdf TEXT
            )
        ''')
        conn.commit()

def insert_announcement(ann: Announcement) -> bool:
    """Inserts a new announcement. Returns True if successful, False if duplicate."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO announcements (seq, exchange, time, symbol, company, type, pdf)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ann.seq, ann.exchange, ann.time, ann.symbol, ann.company, ann.type, ann.pdf))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # The Sequence ID already exists

def get_all_announcements(limit=500):
    """Loads the most recent announcements for the GUI to display."""
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT time, symbol, company, type, seq, pdf, exchange 
            FROM announcements ORDER BY time DESC LIMIT ?
        ''', (limit,))
        
        return [Announcement(
            time=r[0], symbol=r[1], company=r[2], type=r[3], 
            seq=r[4], pdf=r[5], exchange=r[6]
        ) for r in cursor.fetchall()]