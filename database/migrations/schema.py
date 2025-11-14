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

        # ==================== Time Tracking Tables ====================

        # جدول WorkSchedule (ساعت کاری کارمندان)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS WorkSchedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time TEXT NOT NULL DEFAULT '10:00',
                end_time TEXT NOT NULL DEFAULT '19:00',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
            );
        """)

        # جدول Holidays (تعطیلات)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                holiday_date TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                holiday_type TEXT CHECK( holiday_type IN ('weekly', 'occasional') ) NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # جدول DailyActivities (فعالیت‌های روزانه از پیش تعریف شده)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DailyActivities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_key TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                icon TEXT,
                max_duration_minutes INTEGER,
                is_fixed_duration INTEGER DEFAULT 0,
                affects_salary INTEGER DEFAULT 0,
                description TEXT
            );
        """)

        # جدول WorkSessions (سشن‌های کاری - تایمرها)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS WorkSessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_type TEXT CHECK( session_type IN ('task', 'daily_activity', 'idle') ) NOT NULL,
                reference_id INTEGER,
                activity_key TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_minutes INTEGER,
                date TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
                FOREIGN KEY (reference_id) REFERENCES Tasks (id) ON DELETE SET NULL
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


def seed_daily_activities():
    """ثبت فعالیت‌های روزانه پیش‌فرض"""
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        activities = [
            ('lunch_prayer', '🍽 نهار و نماز', '🍽', 60, 1, 0, 'زمان نهار و نماز روزانه (60 دقیقه ثابت)'),
            ('break', '☕ استراحت', '☕', None, 0, 1, 'استراحت - در حقوق و امتیاز اثرگذار'),
            ('idle', '⏸ بیکاری', '⏸', None, 0, 0, 'زمانی که کاری برای انجام ندارد')
        ]

        for activity in activities:
            cursor.execute("""
                INSERT OR IGNORE INTO DailyActivities
                (activity_key, display_name, icon, max_duration_minutes, is_fixed_duration, affects_salary, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, activity)

        conn.commit()
        print("✅ فعالیت‌های روزانه با موفقیت ثبت شدند")
        return True

    except Exception as e:
        print(f"❌ خطا در ثبت فعالیت‌های روزانه: {e}")
        return False
    finally:
        conn.close()


def seed_weekly_holidays():
    """ثبت تعطیلات هفتگی (جمعه‌ها)"""
    conn = create_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # ثبت جمعه‌ها به عنوان تعطیلی هفتگی
        # این یک نمونه است - در عمل، جمعه‌ها را باید به صورت دینامیک چک کنیم
        cursor.execute("""
            INSERT OR IGNORE INTO Holidays (holiday_date, title, holiday_type)
            VALUES ('FRIDAY', 'جمعه', 'weekly')
        """)

        conn.commit()
        print("✅ تعطیلات هفتگی با موفقیت ثبت شدند")
        return True

    except Exception as e:
        print(f"❌ خطا در ثبت تعطیلات هفتگی: {e}")
        return False
    finally:
        conn.close()


def setup_database():
    """راه‌اندازی کامل دیتابیس"""
    print("🔄 در حال راه‌اندازی دیتابیس...")
    if create_tables():
        seed_admin()
        seed_daily_activities()
        seed_weekly_holidays()
        print("✅ دیتابیس با موفقیت راه‌اندازی شد")
        return True
    return False
