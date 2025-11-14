#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت debug برای بررسی WorkSessions
"""

from database.connection import create_connection
from datetime import datetime

def debug_worksessions():
    """بررسی تمام WorkSessions در دیتابیس"""
    print("\n" + "="*60)
    print("🔍 Debug WorkSessions")
    print("="*60)

    conn = create_connection()
    cursor = conn.cursor()

    # نمایش تمام Users
    print("\n👥 کاربران:")
    cursor.execute("SELECT id, telegram_id, name FROM Users")
    users = cursor.fetchall()
    for user in users:
        print(f"   ID: {user[0]}, Telegram: {user[1]}, نام: {user[2]}")

    # نمایش تمام Tasks
    print("\n📋 کارها:")
    cursor.execute("SELECT id, title, assigned_to_id, status FROM Tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        print(f"   ID: {task[0]}, عنوان: {task[1]}, اختصاص به: {task[2]}, وضعیت: {task[3]}")

    # نمایش تمام WorkSessions
    print("\n⏱️ WorkSessions:")
    cursor.execute("""
        SELECT id, user_id, session_type, reference_id, activity_key,
               start_time, end_time, duration_minutes, is_active, date
        FROM WorkSessions
        ORDER BY id DESC
        LIMIT 20
    """)
    sessions = cursor.fetchall()

    if not sessions:
        print("   ❌ هیچ WorkSession یافت نشد!")
    else:
        for session in sessions:
            session_id, user_id, s_type, ref_id, act_key, start, end, duration, active, date = session

            # محاسبه زمان سپری شده برای session های فعال
            if end is None and start:
                try:
                    start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                    now_dt = datetime.now()
                    elapsed = int((now_dt - start_dt).total_seconds() / 60)
                    duration_display = f"{elapsed}د (فعال)"
                except:
                    duration_display = "خطا در محاسبه"
            else:
                duration_display = f"{duration}د" if duration else "0د"

            active_display = "✅" if active == 1 else "❌"

            print(f"\n   Session ID: {session_id}")
            print(f"   └─ کاربر: {user_id}")
            print(f"   └─ نوع: {s_type}")
            print(f"   └─ reference_id: {ref_id}")
            print(f"   └─ activity_key: {act_key}")
            print(f"   └─ شروع: {start}")
            print(f"   └─ پایان: {end or 'در حال انجام'}")
            print(f"   └─ مدت: {duration_display}")
            print(f"   └─ فعال: {active_display}")
            print(f"   └─ تاریخ: {date}")

    # محاسبه زمان سپری شده برای هر task
    print("\n📊 زمان سپری شده برای هر کار:")
    cursor.execute("""
        SELECT t.id, t.title, u.id as user_id, u.name,
               COALESCE(SUM(
                   CASE
                       WHEN ws.end_time IS NULL THEN
                           CAST((JULIANDAY(datetime('now')) - JULIANDAY(ws.start_time)) * 24 * 60 AS INTEGER)
                       ELSE
                           ws.duration_minutes
                   END
               ), 0) as total_minutes
        FROM Tasks t
        LEFT JOIN Users u ON t.assigned_to_id = u.id
        LEFT JOIN WorkSessions ws ON ws.reference_id = t.id AND ws.user_id = u.id AND ws.session_type = 'task'
        GROUP BY t.id, u.id
        HAVING total_minutes > 0 OR t.status IN ('in_progress', 'pending')
        ORDER BY t.id DESC
    """)
    results = cursor.fetchall()

    if not results:
        print("   ❌ هیچ زمانی ثبت نشده!")
    else:
        for row in results:
            task_id, title, user_id, name, total = row
            print(f"   کار #{task_id}: {title}")
            print(f"   └─ کاربر: {name} (ID: {user_id})")
            print(f"   └─ زمان سپری شده: {total}د")

    conn.close()

    print("\n" + "="*60)
    print("✅ Debug تمام شد")
    print("="*60 + "\n")

if __name__ == "__main__":
    debug_worksessions()
