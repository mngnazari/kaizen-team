# handlers/admin/user_management_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.user_service import UserService


async def show_user_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی مدیریت کاربران"""
    query = update.callback_query
    await query.answer()

    # دریافت همه کاربران (غیر از ادمین)
    users = UserService.get_all_users()

    if not users:
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")]]
        await query.edit_message_text(
            "👥 هیچ کاربری وجود ندارد.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = "👥 **مدیریت کاربران**\n\n"
    text += "لیست کاربران ثبت‌شده:\n\n"

    keyboard = []
    for user in users:
        status_icon = "✅" if user.get('is_employee') == 1 else "⏳"
        button_text = f"{status_icon} {user.get('name')}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"user_{user.get('telegram_id')}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش جزئیات کاربر"""
    query = update.callback_query
    await query.answer()

    telegram_id = int(query.data.split('_')[1])
    user = UserService.get_user_info(telegram_id)

    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    text = f"👤 **اطلاعات کاربر**\n\n"
    text += f"📝 نام: {user.get('name')}\n"
    text += f"📱 شماره تلفن: {user.get('phone_number') if user.get('phone_number') else 'ثبت نشده'}\n"
    text += f"🆔 Telegram ID: {telegram_id}\n"
    text += f"📅 تاریخ ثبت‌نام: {user.get('registration_date')}\n"
    text += f"📊 وضعیت: {'کارمند ✅' if user.get('is_employee') == 1 else 'در انتظار تأیید ⏳'}\n"

    if user.get('approved_date'):
        text += f"✅ تاریخ تأیید: {user.get('approved_date')}\n"

    keyboard = []

    if user.get('is_employee') == 0:
        keyboard.append([InlineKeyboardButton("✅ تبدیل به کارمند", callback_data=f"approve_{telegram_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="user_management")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def request_approval_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست تأیید برای تبدیل به کارمند"""
    query = update.callback_query
    await query.answer()

    telegram_id = int(query.data.split('_')[1])
    user = UserService.get_user_info(telegram_id)

    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    context.user_data['pending_approval_telegram_id'] = telegram_id

    keyboard = [
        [
            InlineKeyboardButton("✅ بله، مطمئنم", callback_data=f"confirm_approve_{telegram_id}"),
            InlineKeyboardButton("❌ خیر، انصراف", callback_data="user_management")
        ]
    ]

    phone_info = f"\n📱 {user.get('phone_number')}" if user.get('phone_number') else ""

    await query.edit_message_text(
        f"⚠️ **تأیید عملیات**\n\n"
        f"آیا مطمئن هستید که می‌خواهید:\n"
        f"👤 {user.get('name')}{phone_info}\n\n"
        f"را به عنوان **کارمند** تأیید کنید؟",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def confirm_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید نهایی و تبدیل به کارمند"""
    query = update.callback_query
    await query.answer()

    telegram_id = int(query.data.split('_')[2])
    user = UserService.get_user_info(telegram_id)

    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    # تبدیل به کارمند
    success = UserService.approve_employee(telegram_id)

    if success:
        await query.edit_message_text(
            f"✅ کاربر **{user.get('name')}** با موفقیت به کارمند تبدیل شد!",
            parse_mode='Markdown'
        )

        # ارسال پیام به کاربر
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text="🎉 تبریک! شما به عنوان کارمند تأیید شدید.\n\n"
                     "اکنون می‌توانید از امکانات سیستم استفاده کنید.\n"
                     "برای شروع /start را بزنید."
            )
        except:
            pass
    else:
        await query.edit_message_text("❌ خطا در تبدیل به کارمند!")
