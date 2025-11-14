# handlers/admin/menu_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import ADMIN_ID
from services.user_service import UserService
from utils.keyboards import get_main_menu_keyboard, get_employee_main_keyboard


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی اصلی - برای ادمین یا کارمند"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # چک ادمین
    if user_id == ADMIN_ID:
        await query.edit_message_text(
            "🏠 **منوی اصلی - مدیریت**",
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        # منوی کارمند
        user = UserService.get_user_info(user_id)
        if user and user.get('is_employee') == 1:  # ✅ اصلاح شد
            await query.edit_message_text(
                "🏠 **منوی اصلی**",
                reply_markup=get_employee_main_keyboard(),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ شما دسترسی به این بخش را ندارید."
            )