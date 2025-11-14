# handlers/admin/manage/manage_menu_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


async def show_manage_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی مدیریت کارها"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("👥 بر اساس کارمند", callback_data="manage_by_employee")],
        [InlineKeyboardButton("📂 بر اساس دسته‌بندی", callback_data="manage_by_category")],
        [InlineKeyboardButton("📊 بر اساس وضعیت", callback_data="manage_by_status")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")]
    ]

    await query.edit_message_text(
        "📊 **مدیریت کارها**\n\n"
        "لطفاً نوع دسته‌بندی را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )