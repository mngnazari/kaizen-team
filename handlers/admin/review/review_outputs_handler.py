# handlers/admin/review/review_outputs_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.work_service import WorkService
from services.file_service import FileService


async def show_employee_outputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش خروجی‌های کارمند (دانش، پیشنهاد، نتایج، امتیاز)"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    admin_telegram_id = query.from_user.id

    # دریافت تمام داده‌های کاری
    all_work_data = WorkService.get_all_work_data(task_id)

    await query.edit_message_text(
        f"📊 **خروجی‌های کارمند**\n\n"
        f"در حال ارسال اطلاعات...",
        parse_mode='Markdown'
    )

    # ========== 1. دانش ==========
    knowledge_data = all_work_data.get('knowledge', [])
    if knowledge_data:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📚 **دانش‌های ثبت شده**",
            parse_mode='Markdown'
        )

        for idx, item in enumerate(knowledge_data, 1):
            if item.get('text_content'):
                await context.bot.send_message(
                    chat_id=admin_telegram_id,
                    text=f"**#{idx}**\n{item['text_content']}",
                    parse_mode='Markdown'
                )

            if item.get('file_id'):
                await FileService.send_file_to_user(
                    context.bot,
                    admin_telegram_id,
                    item['file_id'],
                    item['file_type']
                )
    else:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📚 **دانش‌های ثبت شده**\n\nهیچ دانشی ثبت نشده است.",
            parse_mode='Markdown'
        )

    # ========== 2. پیشنهادات ==========
    suggestion_data = all_work_data.get('suggestion', [])
    if suggestion_data:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n💡 **پیشنهادات ثبت شده**",
            parse_mode='Markdown'
        )

        for idx, item in enumerate(suggestion_data, 1):
            if item.get('text_content'):
                await context.bot.send_message(
                    chat_id=admin_telegram_id,
                    text=f"**#{idx}**\n{item['text_content']}",
                    parse_mode='Markdown'
                )

            if item.get('file_id'):
                await FileService.send_file_to_user(
                    context.bot,
                    admin_telegram_id,
                    item['file_id'],
                    item['file_type']
                )
    else:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n💡 **پیشنهادات ثبت شده**\n\nهیچ پیشنهادی ثبت نشده است.",
            parse_mode='Markdown'
        )

    # ========== 3. نتایج ==========
    results_data = all_work_data.get('results', [])
    if results_data:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📋 **نتایج ثبت شده**",
            parse_mode='Markdown'
        )

        for idx, item in enumerate(results_data, 1):
            if item.get('text_content'):
                await context.bot.send_message(
                    chat_id=admin_telegram_id,
                    text=f"**#{idx}**\n{item['text_content']}",
                    parse_mode='Markdown'
                )

            if item.get('file_id'):
                await FileService.send_file_to_user(
                    context.bot,
                    admin_telegram_id,
                    item['file_id'],
                    item['file_type']
                )
    else:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📋 **نتایج ثبت شده**\n\nهیچ نتیجه‌ای ثبت نشده است.",
            parse_mode='Markdown'
        )

    # ========== 4. امتیاز خود ==========
    # دریافت اطلاعات کار برای گرفتن user_id
    from services.task_service import TaskService
    task = TaskService.get_task(task_id, with_details=True)
    if task:
        user_id = task.get('assigned_to_id')
        self_score_data = WorkService.get_self_score(task_id, user_id)

        if self_score_data:
            score = self_score_data.get('self_score')
            await context.bot.send_message(
                chat_id=admin_telegram_id,
                text=f"━━━━━━━━━━━━━━━━━\n⭐ **امتیاز خود کارمند:** {score}/10",
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=admin_telegram_id,
                text="━━━━━━━━━━━━━━━━━\n⭐ **امتیاز خود کارمند:** ثبت نشده",
                parse_mode='Markdown'
            )

    # دکمه بازگشت
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل بررسی", callback_data=f"review_task_{task_id}")]]
    await context.bot.send_message(
        chat_id=admin_telegram_id,
        text="━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )