#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت برای پاک کردن WorkSession های اشتباه
"""

from database.connection import create_connection

def fix_worksessions():
    """پاک کردن WorkSession هایی که user_id اشتباه دارند"""
    print("\n" + "="*60)
    print("🔧 تصحیح WorkSessions")
    print("="*60)

    conn = create_connection()
    cursor = conn.cursor()

    # پیدا کردن WorkSession هایی که user_id بزرگتر از 1000 است
    # (این‌ها telegram_id هستند، نه user_id)
    cursor.execute("""
        SELECT COUNT(*) FROM WorkSessions
        WHERE user_id > 1000
    """)
    bad_count = cursor.fetchone()[0]

    print(f"\n📊 تعداد WorkSession های اشتباه: {bad_count}")

    if bad_count == 0:
        print("✅ هیچ WorkSession اشتباهی یافت نشد!")
        conn.close()
        return

    # نمایش WorkSession های اشتباه
    cursor.execute("""
        SELECT id, user_id, session_type, reference_id, start_time, end_time
        FROM WorkSessions
        WHERE user_id > 1000
    """)
    bad_sessions = cursor.fetchall()

    print("\n❌ WorkSession های اشتباه:")
    for session in bad_sessions:
        print(f"   Session {session[0]}: user_id={session[1]} (باید 1 یا 2 باشد)")
        print(f"   └─ نوع: {session[2]}, reference_id: {session[3]}")

    # حذف WorkSession های اشتباه
    print(f"\n🗑️ در حال حذف {bad_count} WorkSession اشتباه...")

    cursor.execute("""
        DELETE FROM WorkSessions
        WHERE user_id > 1000
    """)
    conn.commit()

    print(f"✅ {bad_count} WorkSession اشتباه حذف شدند!")

    # نمایش WorkSession های باقی‌مانده
    cursor.execute("SELECT COUNT(*) FROM WorkSessions")
    remaining = cursor.fetchone()[0]
    print(f"\n📊 WorkSession های باقی‌مانده: {remaining}")

    conn.close()

    print("\n" + "="*60)
    print("✅ تصحیح تمام شد!")
    print("="*60)
    print("\n⚠️ لطفاً بات را restart کنید:")
    print("   python main.py")
    print("\n")

if __name__ == "__main__":
    fix_worksessions()
