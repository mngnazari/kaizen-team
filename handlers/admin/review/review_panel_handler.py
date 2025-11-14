# handlers/admin/review/review_panel_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService
from services.review_service import ReviewService


async def show_task_review_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پنل بررسی کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])

    # دریافت اطلاعات کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # دریافت خلاصه نظرات ادمین
    review_summary = ReviewService.get_review_summary(task_id)

    message_text = (
        f"📋 **پنل بررسی کار**\n\n"
        f"**عنوان:** {task.get('title')}\n"
        f"**کارمند:** {task.get('assigned_to_name', 'نامشخص')}\n"
        f"**تاریخ تحویل:** {task.get('completion_date', 'نامشخص')}\n\n"
        f"{review_summary}"
    )

    keyboard = [
        [
            InlineKeyboardButton("📋 شناسنامه کار", callback_data=f"task_profile_{task_id}"),
            InlineKeyboardButton("📊 خروجی‌های کارمند", callback_data=f"employee_outputs_{task_id}")
        ],
        [
            InlineKeyboardButton("💭 نظر شما", callback_data=f"admin_opinion_{task_id}"),
        ],
        [
            InlineKeyboardButton("✅ نقاط مثبت", callback_data=f"admin_positive_{task_id}"),
            InlineKeyboardButton("❌ نقاط منفی", callback_data=f"admin_negative_{task_id}")
        ],
        [
            InlineKeyboardButton("💡 پیشنهاد/انتقاد", callback_data=f"admin_suggestion_{task_id}"),
            InlineKeyboardButton("⭐ امتیازدهی", callback_data=f"admin_score_{task_id}")
        ],
        [
            InlineKeyboardButton("🏁 خاتمه کار", callback_data=f"finalize_task_{task_id}")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت", callback_data="completed_tasks")
        ]
    ]

    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )