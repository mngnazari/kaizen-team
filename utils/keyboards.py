# utils/keyboards.py

"""
کیبوردهای مشترک Telegram
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# ==================== Reply Keyboards (ثابت) ====================

def get_admin_reply_keyboard():
    """کیبورد ثابت برای ادمین"""
    keyboard = [[KeyboardButton("🏠 منوی اصلی")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_employee_reply_keyboard():
    """کیبورد ثابت برای کارمند"""
    keyboard = [[KeyboardButton("🏠 منوی اصلی")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ==================== Admin Keyboards ====================

def get_main_menu_keyboard():
    """کیبورد اصلی ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("➕ تعریف کار", callback_data="define_task"),
            InlineKeyboardButton("✏️ ویرایش کار", callback_data="edit_task")
        ],
        [
            InlineKeyboardButton("📋 مدیریت کارها", callback_data="manage_tasks"),
            InlineKeyboardButton("📂 دسته‌بندی‌ها", callback_data="categories")
        ],
        [
            InlineKeyboardButton("✅ کارهای تحویل شده", callback_data="completed_tasks"),
            InlineKeyboardButton("🗄 کارهای خاتمه‌یافته", callback_data="archived_tasks")
        ],
        [
            InlineKeyboardButton("👥 مدیریت کاربران", callback_data="user_management"),
            InlineKeyboardButton("📊 گزارش روزانه", callback_data="daily_report")
        ],
        [
            InlineKeyboardButton("⚙️ تنظیمات زمان", callback_data="time_settings"),
            InlineKeyboardButton("📊 گزارشات زمان", callback_data="time_reports")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard():
    """کیبورد بازگشت به منو"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")]]
    return InlineKeyboardMarkup(keyboard)


# ==================== Employee Keyboards ====================

def get_employee_main_keyboard():
    """کیبورد اصلی کارمند"""
    keyboard = [
        [
            InlineKeyboardButton("🗂 آرشیو کارها", callback_data="archive_tasks"),
            InlineKeyboardButton("📝 کارها", callback_data="list_tasks")
        ],
        [
            InlineKeyboardButton("⏱ مدیریت زمان", callback_data="time_tracking_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_tasks_keyboard():
    """کیبورد بازگشت به لیست کارها"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_tasks_list")]]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_employee_menu_keyboard():
    """کیبورد بازگشت به منوی اصلی کارمند"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu_employee")]]
    return InlineKeyboardMarkup(keyboard)


# ==================== Task Work Keyboards ====================

def get_task_work_keyboard(task_id, allocated_time, spent_time, is_active=False):
    """
    کیبورد پنل کار

    Args:
        task_id: آیدی کار
        allocated_time: زمان تخصیصی (دقیقه)
        spent_time: زمان سپری شده (دقیقه)
        is_active: آیا این کار در حال انجام است
    """
    from utils.formatters import format_time

    spent_formatted = f"{spent_time}د"
    allocated_formatted = format_time(allocated_time) if allocated_time > 0 else "تعیین نشده"

    # تغییر متن دکمه شروع کار بر اساس وضعیت
    start_button_text = "🚀 شروع کار (درحال انجام)" if is_active else "🚀 شروع کار"

    keyboard = [
        [InlineKeyboardButton(start_button_text, callback_data=f"start_work_{task_id}")],
        [
            InlineKeyboardButton(f"⏱️ کل: {allocated_formatted}", callback_data=f"work_panel_{task_id}"),
            InlineKeyboardButton(f"⌚ سپری شده: {spent_formatted}", callback_data=f"work_panel_{task_id}"),
            InlineKeyboardButton("🔄", callback_data=f"work_panel_{task_id}")
        ],
        [
            InlineKeyboardButton("📚 ثبت دانش", callback_data=f"knowledge_{task_id}"),
            InlineKeyboardButton("💡 پیشنهاد", callback_data=f"suggestion_{task_id}")
        ],
        [
            InlineKeyboardButton("📋 نتایج کار", callback_data=f"results_{task_id}"),
            InlineKeyboardButton("⭐ امتیاز به خود", callback_data=f"self_score_{task_id}")
        ],
        [
            InlineKeyboardButton("🍽 نهار و نماز", callback_data=f"confirm_activity_lunch_prayer"),
            InlineKeyboardButton("☕ استراحت", callback_data=f"confirm_activity_break")
        ],
        [
            InlineKeyboardButton("✅ تحویل کار", callback_data=f"submit_{task_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_tasks_list")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== Phone Request Keyboard ====================

def get_phone_request_keyboard():
    """کیبورد درخواست شماره تلفن"""
    keyboard = [[KeyboardButton("📱 اشتراک‌گذاری شماره تلفن", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# ==================== Confirmation Keyboards ====================

def get_yes_no_keyboard(yes_callback, no_callback="cancel"):
    """کیبورد تأیید/رد"""
    keyboard = [
        [
            InlineKeyboardButton("✅ بله", callback_data=yes_callback),
            InlineKeyboardButton("❌ خیر", callback_data=no_callback)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
