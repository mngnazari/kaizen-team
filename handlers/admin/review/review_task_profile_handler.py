# handlers/admin/review/review_task_profile_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService
from services.file_service import FileService


async def show_task_profile_for_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش شناسنامه کامل کار برای ادمین"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    admin_telegram_id = query.from_user.id

    # دریافت اطلاعات کامل کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # ساخت شناسنامه خلاصه
    summary_text = (
        f"📋 **شناسنامه کار**\n\n"
        f"**📌 عنوان:** {task.get('title')}\n"
        f"**👤 کارمند:** {task.get('assigned_to_name', 'نامشخص')}\n"
        f"**📂 دسته‌بندی:** {task.get('category_name') or 'ندارد'}\n"
        f"**⏱ مدت زمان:** {task.get('duration') or 'تعیین نشده'} دقیقه\n"
        f"**⭐ اهمیت:** {task.get('importance') or 'ندارد'}\n"
        f"**🔥 اولویت:** {task.get('priority') or 'ندارد'}\n"
        f"**📅 تاریخ ایجاد:** {task.get('creation_date')}\n"
        f"**✅ تاریخ تحویل:** {task.get('completion_date')}\n"
    )

    await query.edit_message_text(summary_text, parse_mode='Markdown')

    # ========== 1. توضیحات ==========
    description = task.get('description')
    description_files = FileService.get_section_files(task_id, 'description')

    if description or description_files:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📝 **توضیحات کار**",
            parse_mode='Markdown'
        )

        if description:
            await context.bot.send_message(chat_id=admin_telegram_id, text=description)

        if description_files:
            for file_data in description_files:
                await FileService.send_file_to_user(
                    context.bot,
                    admin_telegram_id,
                    file_data['file_id'],
                    file_data['file_type']
                )
    else:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📝 **توضیحات کار**\n\nتوضیحاتی ثبت نشده است.",
            parse_mode='Markdown'
        )

    # ========== 2. نتایج مورد انتظار ==========
    results = task.get('results')
    results_files = FileService.get_section_files(task_id, 'results')

    if results or results_files:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📊 **نتایج مورد انتظار**",
            parse_mode='Markdown'
        )

        if results:
            await context.bot.send_message(chat_id=admin_telegram_id, text=results)

        if results_files:
            for file_data in results_files:
                await FileService.send_file_to_user(
                    context.bot,
                    admin_telegram_id,
                    file_data['file_id'],
                    file_data['file_type']
                )
    else:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📊 **نتایج مورد انتظار**\n\nنتایجی ثبت نشده است.",
            parse_mode='Markdown'
        )

    # دکمه بازگشت
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل بررسی", callback_data=f"review_task_{task_id}")]]
    await context.bot.send_message(
        chat_id=admin_telegram_id,
        text="━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )