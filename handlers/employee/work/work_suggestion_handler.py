# handlers/employee/work/work_suggestion_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    MessageHandler, filters, CommandHandler
)
from database.models.user import UserModel
from services.work_service import WorkService
from services.file_service import FileService
from utils.constants import WORK_SUGGESTION_ENTRY


async def start_suggestion_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ثبت پیشنهاد"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[1])
    user_telegram_id = query.from_user.id

    # دریافت user_id
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return ConversationHandler.END

    user_id = user.get('id')
    context.user_data['current_task_id'] = task_id

    # نمایش پیشنهادهای قبلی
    previous_suggestions = WorkService.get_task_suggestions(task_id, user_id)

    if previous_suggestions:
        await query.edit_message_text(
            "💡 **پیشنهادهای ثبت شده قبلی:**\n\n"
            "در حال ارسال پیشنهادهای قبلی...",
            parse_mode='Markdown'
        )

        # ارسال تمام پیشنهادهای قبلی
        for idx, suggestion in enumerate(previous_suggestions, 1):
            # ارسال متن
            if suggestion.get('text_content'):
                await context.bot.send_message(
                    chat_id=user_telegram_id,
                    text=f"💡 پیشنهاد #{idx}:\n{suggestion.get('text_content')}"
                )

            # ارسال فایل
            if suggestion.get('file_id') and suggestion.get('file_type'):
                file_id = suggestion.get('file_id')
                file_type = suggestion.get('file_type')

                try:
                    if file_type == 'photo':
                        await context.bot.send_photo(chat_id=user_telegram_id, photo=file_id)
                    elif file_type == 'video':
                        await context.bot.send_video(chat_id=user_telegram_id, video=file_id)
                    elif file_type == 'voice':
                        await context.bot.send_voice(chat_id=user_telegram_id, voice=file_id)
                    elif file_type == 'document':
                        await context.bot.send_document(chat_id=user_telegram_id, document=file_id)
                except Exception as e:
                    await context.bot.send_message(
                        chat_id=user_telegram_id,
                        text=f"⚠️ خطا در ارسال فایل: {str(e)}"
                    )

        # پیام ثبت پیشنهاد جدید
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text=(
                "━━━━━━━━━━━━━━━━━\n\n"
                "💡 **ثبت پیشنهاد جدید**\n\n"
                "لطفاً پیشنهاد جدید را به صورت متن، عکس، ویدیو، فایل یا صدا ارسال کنید.\n\n"
                "برای اتمام، /done را ارسال کنید."
            ),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "💡 **ثبت پیشنهاد**\n\n"
            "لطفاً پیشنهادات خود را برای بهبود این کار به صورت متن، عکس، ویدیو، فایل یا صدا ارسال کنید.\n\n"
            "برای اتمام، /done را ارسال کنید.",
            parse_mode='Markdown'
        )

    return WORK_SUGGESTION_ENTRY


async def receive_suggestion_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پیشنهاد (متن یا فایل)"""
    task_id = context.user_data.get('current_task_id')
    user_telegram_id = update.effective_user.id

    # دریافت user_id
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        await update.message.reply_text("❌ کاربر یافت نشد!")
        return ConversationHandler.END

    user_id = user.get('id')

    # ذخیره متن
    if update.message.text and update.message.text != '/done':
        WorkService.add_suggestion(task_id, user_id, text_content=update.message.text)
        await update.message.reply_text("✅ پیشنهاد ثبت شد!\n\nمی‌توانید پیشنهاد بیشتری اضافه کنید یا /done بزنید.")
        return WORK_SUGGESTION_ENTRY

    # ذخیره فایل
    file_type = FileService.get_file_type_from_message(update.message)
    file_id = FileService.get_file_id_from_message(update.message)

    if file_type and file_id:
        WorkService.add_suggestion(task_id, user_id, file_id=file_id, file_type=file_type)
        await update.message.reply_text("✅ فایل پیشنهاد ثبت شد!\n\nمی‌توانید پیشنهاد بیشتری اضافه کنید یا /done بزنید.")
        return WORK_SUGGESTION_ENTRY

    await update.message.reply_text("❌ لطفاً متن یا فایل ارسال کنید.")
    return WORK_SUGGESTION_ENTRY


async def finish_suggestion_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اتمام ثبت پیشنهاد"""
    task_id = context.user_data.get('current_task_id')

    await update.message.reply_text("✅ ثبت پیشنهاد کامل شد!")

    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل کار", callback_data=f"work_panel_{task_id}")]]
    await update.message.reply_text(
        "برای بازگشت به پنل کار، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_suggestion_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ثبت پیشنهاد"""
    context.user_data.clear()
    await update.message.reply_text("❌ ثبت پیشنهاد لغو شد.")
    return ConversationHandler.END


suggestion_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_suggestion_entry, pattern='^suggestion_')
    ],
    states={
        WORK_SUGGESTION_ENTRY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_suggestion_entry),
            MessageHandler(filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL, receive_suggestion_entry),
            CommandHandler('done', finish_suggestion_entry),
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_suggestion_entry)
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)