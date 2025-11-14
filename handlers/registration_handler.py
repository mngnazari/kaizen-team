# handlers/registration_handler.py

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
)

# ✅ استفاده از Services به جای database_manager
from services.user_service import UserService

# ✅ استفاده از Utils
from utils.constants import GET_FULL_NAME, GET_PHONE
from utils.keyboards import (
    get_main_menu_keyboard, 
    get_employee_main_keyboard, 
    get_phone_request_keyboard
)
from utils.validators import validate_full_name

from config import ADMIN_ID
# handlers/registration_handler.py

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
)

from services.user_service import UserService
from utils.constants import GET_FULL_NAME, GET_PHONE
from utils.keyboards import (
    get_main_menu_keyboard,
    get_employee_main_keyboard,
    get_phone_request_keyboard,
    get_admin_reply_keyboard,      # ✅ اضافه شد
    get_employee_reply_keyboard    # ✅ اضافه شد
)
from utils.validators import validate_full_name

from config import ADMIN_ID

async def check_and_start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """چک می‌کند که آیا کاربر ادمین، کاربر قدیمی یا کاربر جدید است"""
    user_id = update.effective_user.id

    # چک ادمین
    if UserService.is_admin(user_id):
        await update.message.reply_text(
            "👋 خوش آمدید، مدیر عزیز!",
            reply_markup=get_admin_reply_keyboard()  # ✅ کیبورد ثابت
        )
        await update.message.reply_text(
            "📋 منوی مدیریت:",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END

    # بررسی وجود کاربر
    user = UserService.get_user_info(user_id)

    if user:
        # کارمند تأیید شده
        if user.get('is_employee') == 1 and user.get('role') == 'employee':
            await update.message.reply_text(
                f"👋 سلام {user['name']} عزیز!\n\nخوش آمدید.",
                reply_markup=get_employee_reply_keyboard()  # ✅ کیبورد ثابت
            )
            await update.message.reply_text(
                "📋 منوی کاری شما:",
                reply_markup=get_employee_main_keyboard()
            )
            return ConversationHandler.END
        else:
            # در انتظار تأیید
            await update.message.reply_text(
                f"👋 سلام {user['name']} عزیز!\n\n"
                f"⏳ حساب شما در انتظار تأیید مدیر است.\n"
                f"لطفاً صبور باشید.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

    # شروع ثبت‌نام
    await update.message.reply_text(
        "👋 **سلام! خوش آمدید.**\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:\n\n"
        "مثال: علی احمدی",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_FULL_NAME


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند ثبت‌نام"""
    await update.message.reply_text(
        "👋 **سلام! خوش آمدید.**\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد کنید:\n\n"
        "مثال: علی احمدی",
        parse_mode='Markdown'
    )
    return GET_FULL_NAME


async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت نام کامل"""
    full_name = update.message.text.strip()

    # ✅ استفاده از validator
    is_valid, error_message = validate_full_name(full_name)
    
    if not is_valid:
        await update.message.reply_text(error_message)
        return GET_FULL_NAME

    # جداسازی نام و نام خانوادگی
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:])

    context.user_data['first_name'] = first_name
    context.user_data['last_name'] = last_name

    # ✅ استفاده از keyboard از utils
    await update.message.reply_text(
        f"✅ نام: **{full_name}**\n\n"
        f"حالا لطفاً روی دکمه زیر کلیک کنید تا شماره تلفن شما ثبت شود:",
        reply_markup=get_phone_request_keyboard(),  # ✅ از utils
        parse_mode='Markdown'
    )
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت شماره تلفن و ثبت کاربر"""
    contact = update.message.contact

    if not contact:
        await update.message.reply_text(
            "❌ لطفاً از دکمه **📱 اشتراک‌گذاری شماره تلفن** استفاده کنید.",
            parse_mode='Markdown'
        )
        return GET_PHONE

    first_name = context.user_data.get('first_name')
    last_name = context.user_data.get('last_name')
    phone_number = contact.phone_number
    telegram_id = update.effective_user.id

    success = UserService.register_user(telegram_id, first_name, last_name, phone_number)

    if success:
        await update.message.reply_text(
            f"✅ **ثبت‌نام موفق!**\n\n"
            f"👤 نام: {first_name} {last_name}\n"
            f"📱 شماره تلفن: {phone_number}\n\n"
            f"⏳ لطفاً منتظر بمانید تا مدیر شما را تأیید کند.\n"
            f"پس از تأیید، می‌توانید از امکانات بات استفاده کنید.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ خطا در ثبت‌نام! لطفاً دوباره تلاش کنید:\n/start",
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ثبت‌نام"""
    await update.message.reply_text(
        "❌ ثبت‌نام لغو شد.\n\n"
        "برای شروع مجدد، /start را ارسال کنید.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ConversationHandler برای ثبت‌نام
registration_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", check_and_start_registration)
    ],
    states={
        GET_FULL_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name),
            CommandHandler("cancel", cancel_registration)
        ],
        GET_PHONE: [
            MessageHandler(filters.CONTACT, get_phone),
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            CommandHandler("cancel", cancel_registration)
        ]
    },
    fallbacks=[
        CommandHandler("cancel", cancel_registration)
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)
