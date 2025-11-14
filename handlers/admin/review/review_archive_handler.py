# handlers/admin/review/review_archive_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService
from services.review_service import ReviewService
from services.file_service import FileService


async def show_archived_tasks_for_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارهای آرشیو شده"""
    query = update.callback_query
    await query.answer()

    # دریافت کارهای آرشیو شده
    archived_tasks = TaskService.get_archived_tasks()

    if not archived_tasks:
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")]]
        await query.edit_message_text(
            "🗄 **کارهای آرشیو شده**\n\n"
            "هیچ کار آرشیو شده‌ای وجود ندارد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    keyboard = []
    for task in archived_tasks:
        task_id = task.get('id')
        title = task.get('title')
        employee_name = task.get('employee_name', 'نامشخص')

        # دریافت امتیاز ادمین
        admin_score = ReviewService.get_latest_score(task_id)
        score_text = f"({admin_score}/10)" if admin_score else ""

        button_text = f"🗄 {title} - {employee_name} {score_text}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"view_archived_{task_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")])

    await query.edit_message_text(
        f"🗄 **کارهای آرشیو شده** ({len(archived_tasks)} کار)\n\n"
        f"لطفاً کار مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def view_archived_task_for_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات کار آرشیو شده"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])

    # دریافت اطلاعات کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # دریافت خلاصه نظرات
    review_summary = ReviewService.get_review_summary(task_id)

    message_text = (
        f"🗄 **کار آرشیو شده**\n\n"
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
            InlineKeyboardButton("💭 مشاهده نظرات", callback_data=f"admin_review_archived_{task_id}")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت", callback_data="archived_tasks")
        ]
    ]

    await query.edit_message_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_admin_review_for_archived(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش نظرات ادمین برای کار آرشیو شده"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[3])
    admin_telegram_id = query.from_user.id

    # دریافت تمام نظرات
    all_reviews = ReviewService.get_all_reviews(task_id)

    await query.edit_message_text(
        "💭 **نظرات مدیر**\n\n"
        "در حال ارسال...",
        parse_mode='Markdown'
    )

    # ارسال نظرات
    review_types = {
        'opinion': ('💭 نظر کلی', all_reviews.get('opinion', [])),
        'positive': ('✅ نقاط مثبت', all_reviews.get('positive', [])),
        'negative': ('❌ نقاط منفی', all_reviews.get('negative', [])),
        'suggestion': ('💡 پیشنهادات', all_reviews.get('suggestion', [])),
        'score': ('⭐ امتیاز', all_reviews.get('score', []))
    }

    has_any_review = False

    for review_key, (title, reviews) in review_types.items():
        if reviews:
            has_any_review = True
            await context.bot.send_message(
                chat_id=admin_telegram_id,
                text=f"━━━━━━━━━━━━━━━━━\n{title}",
                parse_mode='Markdown'
            )

            if review_key == 'score':
                # امتیاز فقط عدد است
                score = reviews[0].get('admin_score')
                await context.bot.send_message(
                    chat_id=admin_telegram_id,
                    text=f"**امتیاز:** {score}/10",
                    parse_mode='Markdown'
                )
            else:
                # سایر نظرات
                for idx, review in enumerate(reviews, 1):
                    if review.get('text_content'):
                        await context.bot.send_message(
                            chat_id=admin_telegram_id,
                            text=f"**#{idx}**\n{review['text_content']}",
                            parse_mode='Markdown'
                        )

                    if review.get('file_id'):
                        await FileService.send_file_to_user(
                            context.bot,
                            admin_telegram_id,
                            review['file_id'],
                            review['file_type']
                        )

    if not has_any_review:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="ℹ️ هیچ نظری برای این کار ثبت نشده است."
        )

    # دکمه بازگشت
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data=f"view_archived_{task_id}")]]
    await context.bot.send_message(
        chat_id=admin_telegram_id,
        text="━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )