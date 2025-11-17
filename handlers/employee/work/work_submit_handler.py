# handlers/employee/work/work_submit_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.models.user import UserModel
from services.task_service import TaskService
from services.work_service import WorkService


async def submit_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست تحویل کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[1])
    user_telegram_id = query.from_user.id

    # بررسی امکان تحویل
    can_submit, message = TaskService.can_employee_submit(task_id, user_telegram_id)

    if not can_submit:
        # نمایش پیام خطا با راهنمایی کاربر
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به پنل کار", callback_data=f"work_panel_{task_id}")]
        ]

        await query.edit_message_text(
            f"❌ **امکان تحویل کار وجود ندارد!**\n\n"
            f"⚠️ {message}\n\n"
            f"💡 لطفاً ابتدا موارد ذیل را تکمیل کنید:\n"
            f"• حداقل یک نتیجه برای کار ثبت کنید\n"
            f"• امتیاز خود را ثبت کنید",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    # درخواست تأیید
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، تحویل می‌دهم", callback_data=f"confirm_submit_{task_id}"),
            InlineKeyboardButton("❌ خیر", callback_data=f"work_panel_{task_id}")
        ]
    ]

    await query.edit_message_text(
        "⚠️ **تأیید تحویل کار**\n\n"
        "آیا مطمئن هستید که می‌خواهید این کار را تحویل دهید؟\n\n"
        "پس از تحویل، امکان ویرایش وجود نخواهد داشت.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def confirm_submit_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید نهایی و تحویل کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    user_telegram_id = query.from_user.id

    # بررسی مجدد امکان تحویل
    can_submit, message = TaskService.can_employee_submit(task_id, user_telegram_id)

    if not can_submit:
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به پنل کار", callback_data=f"work_panel_{task_id}")]
        ]

        await query.edit_message_text(
            f"❌ **امکان تحویل کار وجود ندارد!**\n\n"
            f"⚠️ {message}\n\n"
            f"💡 لطفاً ابتدا موارد ذیل را تکمیل کنید:\n"
            f"• حداقل یک نتیجه برای کار ثبت کنید\n"
            f"• امتیاز خود را ثبت کنید",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    # تحویل کار
    success = TaskService.submit_task(task_id)

    if success:
        # دریافت اطلاعات کار
        task = TaskService.get_task(task_id, with_details=True)

        await query.edit_message_text(
            f"✅ **کار با موفقیت تحویل داده شد!**\n\n"
            f"📋 {task.get('title')}\n\n"
            f"کار شما در صف بررسی مدیر قرار گرفت.",
            parse_mode='Markdown'
        )

        # اطلاع‌رسانی به ادمین
        try:
            user = UserModel.get_by_telegram_id(user_telegram_id)
            employee_name = user.get('name') if user else 'کارمند'

            admin_id = context.bot_data.get('admin_id')
            if admin_id:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"🔔 **کار جدید تحویل داده شد**\n\n"
                        f"👤 کارمند: {employee_name}\n"
                        f"📋 کار: {task.get('title')}\n\n"
                        f"برای بررسی، به بخش 'کارهای تحویل شده' مراجعه کنید."
                    ),
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"❌ خطا در اطلاع‌رسانی به ادمین: {e}")

    else:
        await query.edit_message_text(
            "❌ خطا در تحویل کار!\n\n"
            "لطفاً دوباره تلاش کنید."
        )


# Callback Query Handlers برای استفاده در main.py
submit_task_callback = CallbackQueryHandler(submit_task, pattern='^submit_')
confirm_submit_callback = CallbackQueryHandler(confirm_submit_task, pattern='^confirm_submit_')