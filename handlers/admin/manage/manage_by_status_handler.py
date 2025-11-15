# handlers/admin/manage/manage_by_status_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService


async def manage_by_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی مدیریت کارها بر اساس وضعیت"""
    query = update.callback_query
    await query.answer()

    # دریافت آمار کلی
    status_stats = TaskService.get_tasks_count_by_status()

    keyboard = [
        [InlineKeyboardButton(
            f"⏳ در انتظار ({status_stats.get('pending', 0)})",
            callback_data="status_list_pending"
        )],
        [InlineKeyboardButton(
            f"🔄 در حال انجام ({status_stats.get('in_progress', 0)})",
            callback_data="status_list_in_progress"
        )],
        [InlineKeyboardButton(
            f"✅ تحویل شده ({status_stats.get('completed', 0)})",
            callback_data="status_list_completed"
        )],
        [InlineKeyboardButton(
            f"⏸ متوقف شده ({status_stats.get('on_hold', 0)})",
            callback_data="status_list_on_hold"
        )],
        [InlineKeyboardButton(
            f"🗄 بایگانی شده ({status_stats.get('archived', 0)})",
            callback_data="status_list_archived"
        )],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="manage_tasks")]
    ]

    await query.edit_message_text(
        "📊 **مدیریت کارها بر اساس وضعیت**\n\n"
        "وضعیت مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_tasks_by_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کارها بر اساس وضعیت مشخص"""
    query = update.callback_query
    await query.answer()

    # استخراج وضعیت از callback_data
    # callback_data format: "status_list_pending" or "status_list_in_progress"
    parts = query.data.split('_')
    status = '_'.join(parts[2:])  # Join all parts after "status_list_"

    # نقشه برای نمایش فارسی
    status_names = {
        'pending': 'در انتظار',
        'in_progress': 'در حال انجام',
        'completed': 'تحویل شده',
        'on_hold': 'متوقف شده',
        'archived': 'بایگانی شده'
    }

    status_emoji = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'on_hold': '⏸',
        'archived': '🗄'
    }

    status_name = status_names.get(status, 'نامشخص')
    emoji = status_emoji.get(status, '❓')

    # دریافت کارها
    tasks = TaskService.get_tasks_by_status(status)

    if not tasks:
        await query.edit_message_text(
            f"{emoji} **هیچ کاری با وضعیت '{status_name}' یافت نشد!**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_status")
            ]]),
            parse_mode='Markdown'
        )
        return

    keyboard = []
    for task in tasks:
        task_id = task.get('id')
        title = task.get('title')
        assigned_to_name = task.get('assigned_to_name', 'تخصیص نیافته')
        category_name = task.get('category_name', 'بدون دسته‌بندی')

        button_text = f"{emoji} {title} - {assigned_to_name} ({category_name})"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"view_task_{task_id}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_status")
    ])

    await query.edit_message_text(
        f"{emoji} **کارهای {status_name}**\n\n"
        f"تعداد: {len(tasks)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
