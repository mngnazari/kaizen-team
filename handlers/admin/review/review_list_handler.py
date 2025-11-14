# handlers/admin/review/review_list_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService


async def show_completed_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارهای تحویل شده برای بررسی"""
    query = update.callback_query
    await query.answer()

    # دریافت کارهای تحویل شده
    completed_tasks = TaskService.get_completed_submitted_tasks()

    if not completed_tasks:
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")]]
        await query.edit_message_text(
            "✅ **کارهای تحویل شده**\n\n"
            "در حال حاضر هیچ کار تحویل شده‌ای برای بررسی وجود ندارد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    keyboard = []
    for task in completed_tasks:
        task_id = task.get('id')
        title = task.get('title')
        employee_name = task.get('employee_name', 'نامشخص')
        completion_date = task.get('completion_date', 'نامشخص')

        button_text = f"📋 {title} - {employee_name}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"review_task_{task_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")])

    await query.edit_message_text(
        f"✅ **کارهای تحویل شده** ({len(completed_tasks)} کار)\n\n"
        f"لطفاً کار مورد نظر را برای بررسی انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )