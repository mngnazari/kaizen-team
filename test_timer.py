#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت تست برای پیدا کردن مشکل تایمر
"""

from database.connection import create_connection
from database.models.user import UserModel
from database.models.work_session import WorkSessionModel
from services.time_tracking_service import TimeTrackingService

def test_database_tables():
    """تست وجود جدول‌های مورد نیاز"""
    print("\n" + "="*60)
    print("📋 بررسی جدول‌های دیتابیس")
    print("="*60)

    conn = create_connection()
    cursor = conn.cursor()

    tables = ['WorkSessions', 'DailyActivities', 'WorkSchedule', 'Holidays']

    for table in tables:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))
        exists = cursor.fetchone() is not None
        status = "✅" if exists else "❌"
        print(f"{status} {table}")

        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   → تعداد رکورد: {count}")

    conn.close()

def test_work_session_model():
    """تست WorkSessionModel"""
    print("\n" + "="*60)
    print("🔍 تست WorkSessionModel")
    print("="*60)

    try:
        # تست با یک user_id تستی
        test_user_id = 1

        session = WorkSessionModel.get_active_session(test_user_id)
        print(f"✅ get_active_session کار می‌کند")
        print(f"   → نتیجه: {session}")

    except Exception as e:
        print(f"❌ خطا در WorkSessionModel: {e}")

def test_time_tracking_service():
    """تست TimeTrackingService"""
    print("\n" + "="*60)
    print("🔍 تست TimeTrackingService")
    print("="*60)

    try:
        # تست با یک user_id تستی
        test_user_id = 1

        status = TimeTrackingService.get_current_status(test_user_id)
        print(f"✅ get_current_status کار می‌کند")
        print(f"   → is_working: {status.get('is_working')}")
        print(f"   → message: {status.get('message')}")

    except Exception as e:
        print(f"❌ خطا در TimeTrackingService: {e}")
        import traceback
        traceback.print_exc()

def test_handlers_import():
    """تست import کردن handler ها"""
    print("\n" + "="*60)
    print("📦 تست Import Handler ها")
    print("="*60)

    try:
        from handlers.employee.work.work_timer_handler import start_work_timer
        print("✅ work_timer_handler import شد")
    except Exception as e:
        print(f"❌ خطا در import work_timer_handler: {e}")
        import traceback
        traceback.print_exc()

    try:
        from handlers.employee.time_tracking_handler import show_time_tracking_menu
        print("✅ time_tracking_handler import شد")
    except Exception as e:
        print(f"❌ خطا در import time_tracking_handler: {e}")
        import traceback
        traceback.print_exc()

def test_main_handlers():
    """بررسی handler های ثبت شده در main.py"""
    print("\n" + "="*60)
    print("🔧 بررسی main.py")
    print("="*60)

    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        handlers_to_check = [
            'start_work_timer',
            'confirm_end_work_day',
            'confirm_activity_lunch_prayer',
            'confirm_activity_break'
        ]

        for handler in handlers_to_check:
            if handler in content:
                print(f"✅ {handler} در main.py موجود است")
            else:
                print(f"❌ {handler} در main.py موجود نیست!")

    except Exception as e:
        print(f"❌ خطا در خواندن main.py: {e}")

def show_users():
    """نمایش کاربران موجود"""
    print("\n" + "="*60)
    print("👥 کاربران موجود در دیتابیس")
    print("="*60)

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, telegram_id, name, role FROM Users")
    users = cursor.fetchall()

    if users:
        for user in users:
            print(f"ID: {user[0]}, Telegram ID: {user[1]}, نام: {user[2]}, نقش: {user[3]}")
    else:
        print("❌ هیچ کاربری یافت نشد!")

    conn.close()

def main():
    print("\n🔍 شروع تست سیستم تایمر...\n")

    test_database_tables()
    test_work_session_model()
    test_time_tracking_service()
    test_handlers_import()
    test_main_handlers()
    show_users()

    print("\n" + "="*60)
    print("✅ تست‌ها تمام شد!")
    print("="*60)
    print("\nاگر همه تست‌ها ✅ بودند، مشکل از:")
    print("1. بات restart نشده است")
    print("2. در Telegram دکمه اشتباه زده می‌شود")
    print("3. خطایی در console بات وجود دارد")
    print("\nلطفاً:")
    print("  1. بات را متوقف کنید (Ctrl+C)")
    print("  2. دوباره اجرا کنید: python main.py")
    print("  3. در Telegram به بات /start بزنید")
    print("  4. وارد منوی 'مدیریت زمان' شوید")
    print("  5. روی 'شروع روز کاری' کلیک کنید")
    print("  6. سپس به کارها بروید و روی شروع کار کلیک کنید")
    print("\n")

if __name__ == "__main__":
    main()
