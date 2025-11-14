#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت برای به‌روزرسانی دیتابیس و رفع مشکلات
"""

import sqlite3
from database.connection import create_connection
from database.migrations.schema import setup_database, seed_daily_activities

def check_table_exists(table_name):
    """بررسی وجود جدول"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def check_column_exists(table_name, column_name):
    """بررسی وجود ستون در جدول"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    exists = column_name in columns
    conn.close()
    return exists

def main():
    print("=" * 60)
    print("🔧 شروع به‌روزرسانی دیتابیس...")
    print("=" * 60)

    # چک کردن جدول‌های مهم
    tables_to_check = [
        'WorkSchedule',
        'Holidays',
        'WorkSessions',
        'DailyActivities'
    ]

    print("\n📋 بررسی جدول‌های موجود:")
    for table in tables_to_check:
        exists = check_table_exists(table)
        status = "✅ موجود" if exists else "❌ وجود ندارد"
        print(f"  {table}: {status}")

    # اجرای setup_database
    print("\n🔨 در حال ایجاد/به‌روزرسانی جدول‌ها...")
    try:
        setup_database()
        print("✅ جدول‌ها با موفقیت ایجاد/به‌روزرسانی شدند")
    except Exception as e:
        print(f"❌ خطا در ایجاد جدول‌ها: {e}")
        return

    # Seed کردن DailyActivities
    print("\n🌱 در حال پر کردن DailyActivities...")
    try:
        seed_daily_activities()
        print("✅ DailyActivities با موفقیت پر شد")
    except Exception as e:
        print(f"❌ خطا در seed کردن: {e}")

    # بررسی نهایی
    print("\n✅ بررسی نهایی:")
    for table in tables_to_check:
        exists = check_table_exists(table)
        status = "✅ OK" if exists else "❌ FAILED"
        print(f"  {table}: {status}")

    # شمارش رکوردها
    print("\n📊 تعداد رکوردها:")
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM DailyActivities")
    activities_count = cursor.fetchone()[0]
    print(f"  DailyActivities: {activities_count} رکورد")

    cursor.execute("SELECT COUNT(*) FROM Users")
    users_count = cursor.fetchone()[0]
    print(f"  Users: {users_count} کاربر")

    cursor.execute("SELECT COUNT(*) FROM Tasks")
    tasks_count = cursor.fetchone()[0]
    print(f"  Tasks: {tasks_count} کار")

    conn.close()

    print("\n" + "=" * 60)
    print("✅ دیتابیس با موفقیت به‌روزرسانی شد!")
    print("=" * 60)
    print("\n⚠️  لطفاً بات را restart کنید:")
    print("   python main.py")
    print("\n")

if __name__ == "__main__":
    main()
