# database/connection.py

import sqlite3
import os
from config import DB_FILE

# مسیر دیتابیس در ریشه پروژه
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), DB_FILE)


def create_connection():
    """
    ایجاد و برگرداندن یک اتصال به دیتابیس SQLite
    
    Returns:
        sqlite3.Connection: اتصال به دیتابیس یا None در صورت خطا
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # برای دسترسی آسان‌تر به ستون‌ها
        return conn
    except sqlite3.Error as e:
        print(f"❌ خطا در اتصال به دیتابیس: {e}")
        return None
