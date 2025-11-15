#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تست محاسبه زمان سپری شده
"""

from database.connection import create_connection
from datetime import datetime

def test_time_calculation():
    """تست محاسبه زمان برای تمام کارها"""
    print("\n" + "="*60)
    print("🧪 تست محاسبه زمان سپری شده")
    print("="*60)

    conn = create_connection()
    cursor = conn.cursor()

    # دریافت تمام کارهای فعال
    cursor.execute("""
        SELECT id, title, assigned_to_id, status
        FROM Tasks
        WHERE status IN ('in_progress', 'pending')
    """)
    tasks = cursor.fetchall()

    for task_id, title, user_id, status in tasks:
        print(f"\n📋 کار: {title} (ID: {task_id})")
        print(f"   کاربر: {user_id}, وضعیت: {status}")

        # دریافت WorkSession های این کار
        cursor.execute("""
            SELECT id, start_time, end_time, duration_minutes, is_active
            FROM WorkSessions
            WHERE session_type = 'task' AND reference_id = ? AND user_id = ?
        """, (task_id, user_id))
        sessions = cursor.fetchall()

        print(f"   تعداد Session ها: {len(sessions)}")

        if len(sessions) == 0:
            print(f"   ⚠️ هیچ WorkSession یافت نشد!")
            continue

        # محاسبه زمان سپری شده (همان کد از work_panel_handler)
        spent_time = 0
        for session in sessions:
            session_id, start_time, end_time, duration_minutes, is_active = session
            print(f"\n   Session {session_id}:")
            print(f"   ├─ شروع: {start_time}")
            print(f"   ├─ پایان: {end_time or 'در حال انجام'}")
            print(f"   ├─ duration_minutes: {duration_minutes}")
            print(f"   └─ is_active: {is_active}")

            if end_time is None:
                # Session فعال
                if start_time:
                    try:
                        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                        now_dt = datetime.now()
                        elapsed = int((now_dt - start_dt).total_seconds() / 60)
                        print(f"   └─ ✅ زمان محاسبه شده: {elapsed} دقیقه")
                        spent_time += elapsed
                    except Exception as e:
                        print(f"   └─ ❌ خطا در محاسبه: {e}")
            else:
                # Session تمام شده
                if duration_minutes and duration_minutes > 0:
                    print(f"   └─ ✅ زمان ثبت شده: {duration_minutes} دقیقه")
                    spent_time += duration_minutes
                else:
                    print(f"   └─ ⚠️ duration_minutes صفر یا None است!")

        print(f"\n   📊 مجموع زمان سپری شده: {spent_time} دقیقه")
        print(f"   📊 فرمت نمایش: \"{spent_time} دقیقه\"" if spent_time > 0 else "0 دقیقه")

    conn.close()

    print("\n" + "="*60)
    print("✅ تست تمام شد")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_time_calculation()
