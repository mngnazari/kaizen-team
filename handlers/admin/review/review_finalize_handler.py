# handlers/admin/review/review_finalize_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService


async def finalize_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست خاتمه کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])

    # بررسی امکان خاتمه
    can_finalize, message = TaskService.can_admin_finalize(task_id)

    if not can_finalize:
        await query.answer(message, show_alert=True)
        return

    # درخواست تأیید
    task = TaskService.get_task(task_id, with_details=True)

    keyboard = [
        [
            InlineKeyboardButton("✅ بله، خاتمه می‌دهم", callback_data=f"confirm_finalize_{task_id}"),
            InlineKeyboardButton("❌ خیر", callback_data=f"review_task_{task_id}")
        ]
    ]

    await query.edit_message_text(
        f"⚠️ **تأیید خاتمه کار**\n\n"
        f"📋 {task.get('title')}\n"
        f"👤 {task.get('assigned_to_name')}\n\n"
        f"آیا مطمئن هستید که می‌خواهید این کار را خاتمه دهید و به آرشیو منتقل کنید؟\n\n"
        f"پس از خاتمه، کار به بخش آرشیو منتقل می‌شود.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def confirm_finalize_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید نهایی و خاتمه کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])

    # بررسی مجدد امکان خاتمه
    can_finalize, message = TaskService.can_admin_finalize(task_id)

    if not can_finalize:
        await query.edit_message_text(f"❌ {message}")
        return

    # خاتمه کار
    success = TaskService.finalize_task(task_id)

    if success:
        task = TaskService.get_task(task_id, with_details=True)

        await query.edit_message_text(
            f"✅ **کار با موفقیت خاتمه یافت!**\n\n"
            f"📋 {task.get('title')}\n"
            f"👤 {task.get('assigned_to_name')}\n\n"
            f"این کار به آرشیو منتقل شد.",
            parse_mode='Markdown'
        )

        # اطلاع‌رسانی به کارمند
        try:
            employee_telegram_id = task.get('assigned_to_id')
            if employee_telegram_id:
                from database.models.user import UserModel
                user = UserModel.get_by_id(employee_telegram_id)
                if user:
                    await context.bot.send_message(
                        chat_id=user.get('telegram_id'),
                        text=(
                            f"🎉 **کار شما خاتمه یافت!**\n\n"
                            f"📋 {task.get('title')}\n\n"
                            f"این کار به آرشیو منتقل شد.\n"
                            f"برای مشاهده نظرات مدیر، به بخش 'آرشیو کارها' مراجعه کنید."
                        ),
                        parse_mode='Markdown'
                    )
        except Exception as e:
            print(f"❌ خطا در اطلاع‌رسانی به کارمند: {e}")

    else:
        await query.edit_message_text(
            "❌ خطا در خاتمه کار!\n\n"
            "لطفاً دوباره تلاش کنید."
        )