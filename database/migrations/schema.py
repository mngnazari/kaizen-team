# database/migrations/schema.py

from database.connection import create_connection
from config import ADMIN_ID
from datetime import datetime


def create_tables():
    """ایجاد تمام جداول دیتابیس"""
    conn = create_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # جدول Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                name TEXT NOT NULL,
                phone_number TEXT,
                role TEXT CHECK( role IN ('admin', 'employee', 'pending') ) NOT NULL DEFAULT 'pending',
                is_employee INTEGER DEFAULT 0,
                registration_date TEXT,
                approved_date TEXT
            );
        """)
        
        # جدول Categories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """)
        
        # جدول Tasks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                assigned_to_id INTEGER,
                assigned_by_id INTEGER,
                duration TEXT,
                results TEXT,
                importance INTEGER,
                priority INTEGER,
                status TEXT CHECK( status IN ('pending', 'in_progress', 'completed', 'on_hold', 'archived') ) NOT NULL DEFAULT 'pending',
                creation_date TEXT,
                completion_date TEXT,
                category_id INTEGER,
                is_submitted INTEGER DEFAULT 0,
                is_finalized INTEGER DEFAULT 0,
                FOREIGN KEY (assigned_to_id) REFERENCES Users (id),
                FOREIGN KEY (assigned_by_id) REFERENCES Users (id),
                FOREIGN KEY (category_id) REFERENCES Categories (id)
            );
        """)
        
        # جدول TaskAttachments (فایل‌های ضمیمه اصلی کار)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TaskAttachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                file_type TEXT,
                FOREIGN KEY (task_id) REFERENCES Tasks (id) ON DELETE CASCADE
            );
        """)
        
        # جدول TaskSectionFiles (فایل‌های مربوط به بخش‌های خاص)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TaskSectionFiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                section_type TEXT CHECK( section_type IN ('results', 'description') ) NOT NULL,
                file_id TEXT NOT NULL,
                file_type TEXT,
                FOREIGN KEY (task_id) REFERENCES Tasks (id) ON DELETE CASCADE
            );
        """)
        
        # جدول TaskActivities (فعالیت‌های کاری)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TaskActivities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                FOREIGN KEY (user_id) REFERENCES Users (id),
                FOREIGN KEY (task_id) REFERENCES Tasks (id) ON DELETE CASCADE
            );
        """)
        
        # جدول TaskWorkData (دانش، پیشنهاد، نتایج کارمند)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TaskWorkData (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                data_type TEXT CHECK( data_type IN ('knowledge', 'suggestion', 'results') ) NOT NULL,
                text_content TEXT,
                file_id TEXT,
                file_type TEXT,
                timestamp TEXT,
                FOREIGN KEY (task_id) REFERENCES Tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES Users (id)
            );
        """)
        
        # جدول TaskScores (امتیازات خود کارمند)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TaskScores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                self_score INTEGER,
                timestamp TEXT,
                FOREIGN KEY (task_id) REFERENCES Tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES Users (id)
            );
        """)
        
        # جدول AdminReviews (نظرات ادمین)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AdminReviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                admin_id INTEGER NOT NULL,
                review_type TEXT CHECK( review_type IN ('opinion', 'positive', 'negative', 'suggestion', 'score') ) NOT NULL,
                text_content TEXT,
                file_id TEXT,
                file_type TEXT,
                admin_score INTEGER,
                timestamp TEXT,
                FOREIGN KEY (task_id) REFERENCES Tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (admin_id) REFERENCES Users (id)
            );
        """)
        
        conn.commit()
        print("✅ جداول با موفقیت ایجاد شدند")
        return True
        
    except Exception as e:
        print(f"❌ خطا در ایجاد جداول: {e}")
        return False
    finally:
        conn.close()


def seed_admin():
    """ثبت ادمین اولیه در دیتابیس"""
    conn = create_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO Users (telegram_id, name, role, is_employee, registration_date) 
            VALUES (?, ?, ?, ?, ?)
        """, (ADMIN_ID, "مدیر سیستم", "admin", 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        print("✅ ادمین با موفقیت ثبت شد")
        return True
        
    except Exception as e:
        print(f"❌ خطا در ثبت ادمین: {e}")
        return False
    finally:
        conn.close()


def setup_database():
    """راه‌اندازی کامل دیتابیس"""
    print("🔄 در حال راه‌اندازی دیتابیس...")
    if create_tables():
        seed_admin()
        print("✅ دیتابیس با موفقیت راه‌اندازی شد")
        return True
    return False
