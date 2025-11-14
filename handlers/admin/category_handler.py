# handlers/admin/category_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters, \
    CommandHandler
from database.models.category import CategoryModel

GET_CATEGORY_NAME = 0


async def show_categories_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی دسته‌بندی‌ها"""
    query = update.callback_query
    await query.answer()

    categories = CategoryModel.get_all()

    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"category_{cat['id']}")])

    keyboard.append([InlineKeyboardButton("➕ تعریف دسته‌بندی جدید", callback_data="new_category")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📂 مدیریت دسته‌بندی‌ها:", reply_markup=reply_markup)


async def start_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تعریف دسته‌بندی جدید"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "لطفا عنوان دسته‌بندی جدید را وارد کنید:\n\n"
        "برای لغو عملیات، /cancel را ارسال کنید."
    )
    return GET_CATEGORY_NAME


async def save_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره دسته‌بندی جدید"""
    category_name = update.message.text.strip()

    if not category_name:
        await update.message.reply_text("❌ نام دسته‌بندی نمی‌تواند خالی باشد!")
        return GET_CATEGORY_NAME

    # بررسی وجود دسته‌بندی
    existing = CategoryModel.get_by_name(category_name)
    if existing:
        await update.message.reply_text("❌ این دسته‌بندی قبلاً وجود دارد.")
        return GET_CATEGORY_NAME

    # ایجاد دسته‌بندی جدید
    category_id = CategoryModel.create(category_name)

    if category_id:
        await update.message.reply_text(f"✅ دسته‌بندی '{category_name}' با موفقیت ایجاد شد.")
    else:
        await update.message.reply_text("❌ خطا در ایجاد دسته‌بندی!")

    await show_categories_menu_direct(update, context)
    return ConversationHandler.END


async def show_categories_menu_direct(update, context):
    """نمایش مستقیم منوی دسته‌بندی‌ها"""
    categories = CategoryModel.get_all()

    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"category_{cat['id']}")])

    keyboard.append([InlineKeyboardButton("➕ تعریف دسته‌بندی جدید", callback_data="new_category")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📂 مدیریت دسته‌بندی‌ها:", reply_markup=reply_markup)


async def cancel_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو فرآیند تعریف دسته‌بندی"""
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END


category_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_new_category, pattern='^new_category$')
    ],
    states={
        GET_CATEGORY_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_category),
            CommandHandler("cancel", cancel_category)
        ]
    },
    fallbacks=[
        CommandHandler("cancel", cancel_category)
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)