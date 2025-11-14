# handlers/employee/work/work_score_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from database.models.user import UserModel
from services.work_service import WorkService
from utils.constants import WORK_SELF_SCORE_ENTRY
from utils.validators import validate_score


async def start_self_score_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت امتیاز خود"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['current_task_id'] = task_id

    # بررسی امتیاز قبلی
    user_telegram_id = query.from_user.id
    user = UserModel.get_by_telegram_id(user_telegram_id)

    if user:
        user_id = user.get('id')
        previous_score = WorkService.get_self_score(task_id, user_id)

        if previous_score:
            score_value = previous_score.get('self_score')
            message = (
                f"⭐ **امتیازدهی به خود**\n\n"
                f"امتیاز فعلی شما: **{score_value}/10**\n\n"
                f"لطفاً امتیاز جدید خود را از 1 تا 10 وارد کنید:\n\n"
                f"برای لغو، /cancel را ارسال کنید."
            )
        else:
            message = (
                "⭐ **امتیازدهی به خود**\n\n"
                "لطفاً امتیاز خود را از 1 تا 10 وارد کنید:\n\n"
                "برای لغو، /cancel را ارسال کنید."
            )
    else:
        message = (
            "⭐ **امتیازدهی به خود**\n\n"
            "لطفاً امتیاز خود را از 1 تا 10 وارد کنید:\n\n"
            "برای لغو، /cancel را ارسال کنید."
        )

    await query.edit_message_text(message, parse_mode='Markdown')
    return WORK_SELF_SCORE_ENTRY


async def receive_self_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت امتیاز خود"""
    task_id = context.user_data.get('current_task_id')
    user_telegram_id = update.effective_user.id
    score_text = update.message.text.strip()

    # اعتبارسنجی امتیاز
    is_valid, score_value, error_message = validate_score(score_text)

    if not is_valid:
        await update.message.reply_text(error_message)
        return WORK_SELF_SCORE_ENTRY

    # دریافت user_id
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد!")
        return ConversationHandler.END

    user_id = user.get('id')

    # ذخیره امتیاز
    result = WorkService.set_self_score(task_id, user_id, score_value)

    if result:
        await update.message.reply_text(f"✅ امتیاز شما ({score_value}/10) با موفقیت ثبت شد!")
    else:
        await update.message.reply_text("❌ خطا در ثبت امتیاز!")

    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل کار", callback_data=f"work_panel_{task_id}")]]
    await update.message.reply_text(
        "برای بازگشت به پنل کار، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_self_score_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ثبت امتیاز"""
    task_id = context.user_data.get('current_task_id')
    context.user_data.clear()

    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل کار", callback_data=f"work_panel_{task_id}")]]
    await update.message.reply_text(
        "❌ ثبت امتیاز لغو شد.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


score_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_self_score_entry, pattern='^self_score_')
    ],
    states={
        WORK_SELF_SCORE_ENTRY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_self_score),
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_self_score_entry)
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)