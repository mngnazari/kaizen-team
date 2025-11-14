# handlers/admin/review/review_input_handlers.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from config import ADMIN_ID
from services.review_service import ReviewService
from services.file_service import FileService
from utils.constants import (
    ADMIN_REVIEW_OPINION_TEXT,
    ADMIN_REVIEW_POSITIVE_TEXT,
    ADMIN_REVIEW_NEGATIVE_TEXT,
    ADMIN_REVIEW_SUGGESTION_TEXT,
    ADMIN_TASK_SCORE
)
from utils.validators import validate_score


# ==================== نظر کلی ====================

async def start_opinion_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت نظر کلی"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['current_task_id'] = task_id
    context.user_data['review_type'] = 'opinion'

    await query.edit_message_text(
        "💭 **ثبت نظر کلی**\n\n"
        "لطفاً نظر کلی خود را درباره این کار به صورت متن، عکس، ویدیو، فایل یا صدا ارسال کنید.\n\n"
        "برای اتمام، /done را ارسال کنید.",
        parse_mode='Markdown'
    )
    return ADMIN_REVIEW_OPINION_TEXT


# ==================== نقاط مثبت ====================

async def start_positive_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت نقاط مثبت"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['current_task_id'] = task_id
    context.user_data['review_type'] = 'positive'

    await query.edit_message_text(
        "✅ **ثبت نقاط مثبت**\n\n"
        "لطفاً نقاط مثبت کار را به صورت متن، عکس، ویدیو، فایل یا صدا ارسال کنید.\n\n"
        "برای اتمام، /done را ارسال کنید.",
        parse_mode='Markdown'
    )
    return ADMIN_REVIEW_POSITIVE_TEXT


# ==================== نقاط منفی ====================

async def start_negative_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت نقاط منفی"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['current_task_id'] = task_id
    context.user_data['review_type'] = 'negative'

    await query.edit_message_text(
        "❌ **ثبت نقاط منفی**\n\n"
        "لطفاً نقاط منفی یا قابل بهبود را به صورت متن، عکس، ویدیو، فایل یا صدا ارسال کنید.\n\n"
        "برای اتمام، /done را ارسال کنید.",
        parse_mode='Markdown'
    )
    return ADMIN_REVIEW_NEGATIVE_TEXT


# ==================== پیشنهاد/انتقاد ====================

async def start_suggestion_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت پیشنهاد/انتقاد"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['current_task_id'] = task_id
    context.user_data['review_type'] = 'suggestion'

    await query.edit_message_text(
        "💡 **ثبت پیشنهاد/انتقاد**\n\n"
        "لطفاً پیشنهادات یا انتقادات خود را به صورت متن، عکس، ویدیو، فایل یا صدا ارسال کنید.\n\n"
        "برای اتمام، /done را ارسال کنید.",
        parse_mode='Markdown'
    )
    return ADMIN_REVIEW_SUGGESTION_TEXT


# ==================== دریافت نظرات (مشترک) ====================

async def receive_review_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت نظر (متن یا فایل) - برای همه انواع نظرات"""
    task_id = context.user_data.get('current_task_id')
    review_type = context.user_data.get('review_type')

    # ذخیره متن
    if update.message.text and update.message.text != '/done':
        # تشخیص نوع نظر و فراخوانی متد مناسب
        if review_type == 'opinion':
            ReviewService.add_opinion(task_id, ADMIN_ID, text_content=update.message.text)
        elif review_type == 'positive':
            ReviewService.add_positive_points(task_id, ADMIN_ID, text_content=update.message.text)
        elif review_type == 'negative':
            ReviewService.add_negative_points(task_id, ADMIN_ID, text_content=update.message.text)
        elif review_type == 'suggestion':
            ReviewService.add_suggestion(task_id, ADMIN_ID, text_content=update.message.text)

        await update.message.reply_text("✅ ثبت شد!\n\nمی‌توانید مطالب بیشتری اضافه کنید یا /done بزنید.")

        # برگشت به همان state
        state_map = {
            'opinion': ADMIN_REVIEW_OPINION_TEXT,
            'positive': ADMIN_REVIEW_POSITIVE_TEXT,
            'negative': ADMIN_REVIEW_NEGATIVE_TEXT,
            'suggestion': ADMIN_REVIEW_SUGGESTION_TEXT
        }
        return state_map.get(review_type, ADMIN_REVIEW_OPINION_TEXT)

    # ذخیره فایل
    file_type = FileService.get_file_type_from_message(update.message)
    file_id = FileService.get_file_id_from_message(update.message)

    if file_type and file_id:
        if review_type == 'opinion':
            ReviewService.add_opinion(task_id, ADMIN_ID, file_id=file_id, file_type=file_type)
        elif review_type == 'positive':
            ReviewService.add_positive_points(task_id, ADMIN_ID, file_id=file_id, file_type=file_type)
        elif review_type == 'negative':
            ReviewService.add_negative_points(task_id, ADMIN_ID, file_id=file_id, file_type=file_type)
        elif review_type == 'suggestion':
            ReviewService.add_suggestion(task_id, ADMIN_ID, file_id=file_id, file_type=file_type)

        await update.message.reply_text("✅ فایل ثبت شد!\n\nمی‌توانید مطالب بیشتری اضافه کنید یا /done بزنید.")

        state_map = {
            'opinion': ADMIN_REVIEW_OPINION_TEXT,
            'positive': ADMIN_REVIEW_POSITIVE_TEXT,
            'negative': ADMIN_REVIEW_NEGATIVE_TEXT,
            'suggestion': ADMIN_REVIEW_SUGGESTION_TEXT
        }
        return state_map.get(review_type, ADMIN_REVIEW_OPINION_TEXT)

    await update.message.reply_text("❌ لطفاً متن یا فایل ارسال کنید.")

    state_map = {
        'opinion': ADMIN_REVIEW_OPINION_TEXT,
        'positive': ADMIN_REVIEW_POSITIVE_TEXT,
        'negative': ADMIN_REVIEW_NEGATIVE_TEXT,
        'suggestion': ADMIN_REVIEW_SUGGESTION_TEXT
    }
    return state_map.get(review_type, ADMIN_REVIEW_OPINION_TEXT)


async def finish_review_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اتمام ثبت نظر"""
    task_id = context.user_data.get('current_task_id')

    await update.message.reply_text("✅ ثبت نظر کامل شد!")

    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل بررسی", callback_data=f"review_task_{task_id}")]]
    await update.message.reply_text(
        "برای بازگشت به پنل بررسی، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== امتیازدهی ====================

async def start_score_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت امتیاز"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['current_task_id'] = task_id

    # بررسی امتیاز قبلی
    previous_score = ReviewService.get_latest_score(task_id)

    if previous_score:
        message = (
            f"⭐ **امتیازدهی**\n\n"
            f"امتیاز فعلی: **{previous_score}/10**\n\n"
            f"لطفاً امتیاز جدید خود را از 1 تا 10 وارد کنید:\n\n"
            f"برای لغو، /cancel را ارسال کنید."
        )
    else:
        message = (
            "⭐ **امتیازدهی**\n\n"
            "لطفاً امتیاز خود را از 1 تا 10 وارد کنید:\n\n"
            "برای لغو، /cancel را ارسال کنید."
        )

    await query.edit_message_text(message, parse_mode='Markdown')
    return ADMIN_TASK_SCORE


async def receive_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت امتیاز"""
    task_id = context.user_data.get('current_task_id')
    score_text = update.message.text.strip()

    # اعتبارسنجی امتیاز
    is_valid, score_value, error_message = validate_score(score_text)

    if not is_valid:
        await update.message.reply_text(error_message)
        return ADMIN_TASK_SCORE

    # ذخیره امتیاز
    result = ReviewService.add_score(task_id, ADMIN_ID, score_value)

    if result:
        await update.message.reply_text(f"✅ امتیاز ({score_value}/10) با موفقیت ثبت شد!")
    else:
        await update.message.reply_text("❌ خطا در ثبت امتیاز!")

    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل بررسی", callback_data=f"review_task_{task_id}")]]
    await update.message.reply_text(
        "برای بازگشت به پنل بررسی، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== لغو ====================

async def cancel_review_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ثبت نظر"""
    task_id = context.user_data.get('current_task_id')
    context.user_data.clear()

    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل بررسی", callback_data=f"review_task_{task_id}")]]
    await update.message.reply_text(
        "❌ ثبت نظر لغو شد.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


# ==================== ConversationHandler ====================

completed_tasks_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_opinion_entry, pattern='^admin_opinion_'),
        CallbackQueryHandler(start_positive_entry, pattern='^admin_positive_'),
        CallbackQueryHandler(start_negative_entry, pattern='^admin_negative_'),
        CallbackQueryHandler(start_suggestion_entry, pattern='^admin_suggestion_'),
        CallbackQueryHandler(start_score_entry, pattern='^admin_score_'),
    ],
    states={
        ADMIN_REVIEW_OPINION_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_entry),
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, receive_review_entry),
            CommandHandler('done', finish_review_entry),
        ],
        ADMIN_REVIEW_POSITIVE_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_entry),
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, receive_review_entry),
            CommandHandler('done', finish_review_entry),
        ],
        ADMIN_REVIEW_NEGATIVE_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_entry),
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, receive_review_entry),
            CommandHandler('done', finish_review_entry),
        ],
        ADMIN_REVIEW_SUGGESTION_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_entry),
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, receive_review_entry),
            CommandHandler('done', finish_review_entry),
        ],
        ADMIN_TASK_SCORE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_score),
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_review_entry)
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)