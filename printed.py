import os
import shutil
import re

# مسیرهای اصلی
CUSTOMERS_DIR = r"C:\Users\Laser\Desktop\total"
PRINTED_DIR = r"C:\Users\Laser\Desktop\printed"

# تابع کمکی برای نرمال‌سازی نام فایل
def normalize_name(filename):
    name, ext = os.path.splitext(filename)
    name = re.sub(r"\(\d+\)$", "", name)  # حذف (1), (2), ...
    return name.strip().lower()

# جمع‌آوری فایل‌های پرینت‌شده
printed_files = {}
for root, dirs, files in os.walk(PRINTED_DIR):
    for f in files:
        if f.lower().endswith(".stl"):
            printed_files[normalize_name(f)] = os.path.join(root, f)

print(f"تعداد فایل‌های پرینت شده: {len(printed_files)}")

# بررسی مشتری‌ها
for customer in os.listdir(CUSTOMERS_DIR):
    customer_path = os.path.join(CUSTOMERS_DIR, customer)
    if not os.path.isdir(customer_path):
        continue

    printed_subdir = os.path.join(customer_path, "Printed")
    os.makedirs(printed_subdir, exist_ok=True)

    for f in os.listdir(customer_path):
        if not f.lower().endswith(".stl"):
            continue

        norm = normalize_name(f)
        if norm in printed_files:
            src = printed_files[norm]
            dst = os.path.join(printed_subdir, f)

            print(f"انتقال: {f} → {printed_subdir}")
            shutil.move(src, dst)

print("✅ عملیات انتقال فایل‌های پرینت‌شده با موفقیت انجام شد.")
