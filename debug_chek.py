# debug_check.py - این فایل رو در پوشه اصلی پروژه بزار و اجرا کن

import sqlite3

conn = sqlite3.connect('task_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 50)
print("📊 بررسی جدول TaskWorkData")
print("=" * 50)

# همه رکوردها
cursor.execute("SELECT * FROM TaskWorkData ORDER BY timestamp DESC LIMIT 10")
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\nID: {row['id']}")
        print(f"Task ID: {row['task_id']}")
        print(f"User ID: {row['user_id']}")
        print(f"Data Type: {row['data_type']}")
        print(f"Text: {row['text_content']}")
        print(f"File ID: {row['file_id']}")
        print(f"Timestamp: {row['timestamp']}")
        print("-" * 30)
else:
    print("❌ هیچ رکوردی وجود ندارد!")

# شمارش بر اساس نوع
cursor.execute("SELECT data_type, COUNT(*) as count FROM TaskWorkData GROUP BY data_type")
counts = cursor.fetchall()

print("\n📈 آمار:")
for row in counts:
    print(f"  {row['data_type']}: {row['count']} مورد")

conn.close()
