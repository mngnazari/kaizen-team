#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت جامع debug برای یافتن علت زمان 0
"""

from database.connection import create_connection
from datetime import datetime

def debug_everything():
    """بررسی کامل دیتابیس و یافتن مشکل"""
    print("\n" + "="*70)
    print("🔍 DEBUG جامع - یافتن علت زمان 0")
    print("="*70)

    conn = create_connection()
    cursor = conn.cursor()

    # 1. نمایش Users
    print("\n" + "─"*70)
    print("👥 کاربران:")
    print("─"*70)
    cursor.execute("SELECT id, telegram_id, name, role FROM Users")
    users = cursor.fetchall()
    for user in users:
        print(f"   ID: {user[0]:3d} | Telegram: {user[1]:12d} | نام: {user[2]:20s} | نقش: {user[3]}")

    # 2. نمایش Tasks فعال
    print("\n" + "─"*70)
    print("📋 کارهای فعال:")
    print("─"*70)
    cursor.execute("""
        SELECT id, title, assigned_to_id, status, duration
        FROM Tasks
        WHERE status IN ('in_progress', 'pending')
        ORDER BY id DESC
    """)
    tasks = cursor.fetchall()
    for task in tasks:
        print(f"   ID: {task[0]:3d} | عنوان: {task[1]:30s} | کاربر: {task[2]} | وضعیت: {task[3]:15s} | مدت: {task[4]}")

    # 3. نمایش تمام WorkSessions
    print("\n" + "─"*70)
    print("⏱️ تمام WorkSessions (آخرین 10):")
    print("─"*70)
    cursor.execute("""
        SELECT id, user_id, session_type, reference_id, activity_key,
               start_time, end_time, duration_minutes, is_active, date
        FROM WorkSessions
        ORDER BY id DESC
        LIMIT 10
    """)
    sessions = cursor.fetchall()

    for session in sessions:
        session_id, user_id, s_type, ref_id, act_key, start, end, duration, active, date = session

        # محاسبه زمان سپری شده
        if end is None and start:
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                now_dt = datetime.now()
                elapsed = int((now_dt - start_dt).total_seconds() / 60)
                time_display = f"{elapsed}د (فعال)"
            except:
                time_display = "خطا"
        else:
            time_display = f"{duration}د" if duration else "0د"

        active_icon = "✅" if active == 1 else "❌"

        print(f"\n   Session #{session_id}:")
        print(f"   ├─ user_id: {user_id}")
        print(f"   ├─ نوع: {s_type:15s} | reference_id: {ref_id}")
        print(f"   ├─ activity_key: {act_key}")
        print(f"   ├─ شروع: {start}")
        print(f"   ├─ پایان: {end or '───'}")
        print(f"   ├─ مدت: {time_display}")
        print(f"   ├─ is_active: {active_icon} ({active})")
        print(f"   └─ تاریخ: {date}")

    # 4. تست get_active_session برای هر کاربر
    print("\n" + "─"*70)
    print("🔍 تست get_active_session برای هر کاربر:")
    print("─"*70)
    for user in users:
        user_id = user[0]
        user_name = user[2]

        cursor.execute("""
            SELECT id, session_type, reference_id, is_active
            FROM WorkSessions
            WHERE user_id = ? AND is_active = 1
            ORDER BY start_time DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            print(f"   ✅ کاربر {user_name} (ID: {user_id}):")
            print(f"      └─ Session فعال: #{result[0]} | نوع: {result[1]} | ref: {result[2]}")
        else:
            print(f"   ❌ کاربر {user_name} (ID: {user_id}): هیچ session فعالی ندارد")

    # 5. محاسبه زمان سپری شده برای هر کار
    print("\n" + "─"*70)
    print("📊 محاسبه زمان سپری شده برای هر کار:")
    print("─"*70)

    for task in tasks:
        task_id, title, user_id, status, allocated = task

        print(f"\n   📋 کار #{task_id}: {title}")
        print(f"      کاربر: {user_id} | وضعیت: {status} | زمان کل: {allocated}د")

        # یافتن WorkSession های این کار
        cursor.execute("""
            SELECT id, start_time, end_time, duration_minutes, is_active
            FROM WorkSessions
            WHERE session_type = 'task' AND reference_id = ? AND user_id = ?
        """, (task_id, user_id))
        task_sessions = cursor.fetchall()

        print(f"      تعداد Session: {len(task_sessions)}")

        if len(task_sessions) == 0:
            print(f"      ⚠️ هیچ WorkSession یافت نشد!")
            continue

        # محاسبه زمان (همان کد work_panel_handler)
        spent_time = 0
        for sess in task_sessions:
            sess_id, start_time, end_time, duration_minutes, is_active = sess

            if end_time is None:
                if start_time:
                    try:
                        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                        now_dt = datetime.now()
                        elapsed = int((now_dt - start_dt).total_seconds() / 60)
                        spent_time += elapsed
                        print(f"         Session #{sess_id}: {elapsed}د (فعال)")
                    except Exception as e:
                        print(f"         Session #{sess_id}: خطا - {e}")
            else:
                if duration_minutes and duration_minutes > 0:
                    spent_time += duration_minutes
                    print(f"         Session #{sess_id}: {duration_minutes}د (تمام شده)")
                else:
                    print(f"         Session #{sess_id}: 0د (duration_minutes خالی)")

        print(f"      📊 مجموع زمان سپری شده: {spent_time} دقیقه")

        if spent_time == 0:
            print(f"      ⚠️⚠️⚠️ زمان صفر است! علت:")
            if len(task_sessions) == 0:
                print(f"         ❌ هیچ WorkSession یافت نشد")
            else:
                for sess in task_sessions:
                    if sess[2] is not None and (sess[3] is None or sess[3] == 0):
                        print(f"         ❌ Session #{sess[0]}: end_time={sess[2]} اما duration_minutes={sess[3]}")

    conn.close()

    print("\n" + "="*70)
    print("✅ Debug تمام شد")
    print("="*70 + "\n")

if __name__ == "__main__":
    debug_everything()
