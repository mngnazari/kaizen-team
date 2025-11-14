from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import ContextTypes
from services.user_service import UserService
from services.task_service import TaskService
from services.file_service import FileService
from services.work_service import WorkService
from services.review_service import ReviewService


def get_employee_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("کارها", callback_data="list_tasks")],
        [InlineKeyboardButton("آرشیو کارها", callback_data="archive_tasks")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_archived_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کارهای آرشیو شده برای کارمند"""
    query = update.callback_query
    await query.answer()

    user_telegram_id = query.from_user.id

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (user_telegram_id,))
    user_db_id = cursor.fetchone()[0]

    # دریافت کارهای آرشیو شده با امتیاز ادمین
    cursor.execute("""
        SELECT t.id, t.title, COALESCE(ar.admin_score, 'بدون امتیاز') as admin_score
        FROM Tasks t
        LEFT JOIN AdminReviews ar ON t.id = ar.task_id AND ar.review_type = 'score'
        WHERE t.assigned_to_id = ? AND t.status = 'archived'
        ORDER BY t.completion_date DESC
    """, (user_db_id,))

    archived_tasks = cursor.fetchall()
    conn.close()

    if not archived_tasks:
        await query.edit_message_text("هیچ کار آرشیو شده‌ای وجود ندارد.")
        return

    keyboard = []
    for task_id, title, admin_score in archived_tasks:
        score_text = f"({admin_score})" if admin_score != 'بدون امتیاز' else ""
        keyboard.append([
            InlineKeyboardButton(f"{title} {score_text}", callback_data=f"view_archive_{task_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu_employee")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"آرشیو کارها ({len(archived_tasks)} کار):",
        reply_markup=reply_markup
    )


async def view_archived_task_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش جزئیات کار آرشیو شده با نظرات کامل ادمین"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    user_telegram_id = query.from_user.id

    try:
        conn = create_connection()
        cursor = conn.cursor()

        # اطلاعات کار
        cursor.execute("""
            SELECT t.title, t.description, t.duration, t.results, t.importance, 
                   t.priority, t.completion_date, c.name as category_name
            FROM Tasks t
            LEFT JOIN Categories c ON t.category_id = c.id
            WHERE t.id = ?
        """, (task_id,))

        task_info = cursor.fetchone()

        if not task_info:
            await query.edit_message_text("❌ کار یافت نشد!")
            conn.close()
            return

        # نظرات ادمین
        cursor.execute("""
            SELECT review_type, text_content, file_id, file_type, admin_score
            FROM AdminReviews
            WHERE task_id = ?
            ORDER BY review_type
        """, (task_id,))
        admin_reviews = cursor.fetchall()

        # اطلاعات کار
        title, description, duration, results, importance, priority, completion_date, category_name = task_info

        message_text = (
            f"📋 **جزئیات کار آرشیو شده**\n\n"
            f"**عنوان:** {title}\n"
            f"**دسته‌بندی:** {category_name or 'ندارد'}\n"
            f"**مدت زمان:** {duration or 'ندارد'} دقیقه\n"
            f"**نتایج مورد انتظار:** {results or 'ندارد'}\n"
            f"**توضیحات:** {description or 'ندارد'}\n"
            f"**اهمیت:** {importance or 'ندارد'}\n"
            f"**اولویت:** {priority or 'ندارد'}\n"
            f"**تاریخ تکمیل:** {completion_date}\n"
            f"{'—' * 20}\n"
            f"**نظرات مدیر:**\n"
        )

        await query.edit_message_text(message_text, parse_mode='Markdown')

        # اگر نظری ثبت نشده باشد، فقط دکمه بازگشت و متن نمایش داده می‌شود و برمی‌گردد
        if not admin_reviews:
            keyboard = [[InlineKeyboardButton("🔙 بازگشت به آرشیو", callback_data="archive_tasks")]]
            await context.bot.send_message(
                chat_id=user_telegram_id,
                text="⚠️ نظر مدیری برای این کار ثبت نشده است.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # ارسال نظرات ادمین با گروه‌بندی
        review_types = {
            'opinion': '💭 نظر کلی مدیر',
            'positive': '✅ نقاط مثبت',
            'negative': '❌ نقاط منفی',
            'suggestion': '💡 پیشنهادات مدیر',
            'score': '⭐ امتیاز مدیر'
        }

        # گروه‌بندی نظرات بر اساس نوع
        grouped_reviews = {}
        for review_type, text_content, file_id, file_type, admin_score in admin_reviews:
            if review_type not in grouped_reviews:
                grouped_reviews[review_type] = []
            grouped_reviews[review_type].append({
                'text': text_content,
                'file_id': file_id,
                'file_type': file_type,
                'score': admin_score
            })

        # ارسال نظرات به ترتیب
        for review_key, review_title in review_types.items():
            if review_key in grouped_reviews:
                review_data = grouped_reviews[review_key]

                if review_key == 'score':
                    # امتیاز فقط متن است
                    score = review_data[0].get('score', 'ثبت نشده')
                    await context.bot.send_message(
                        chat_id=user_telegram_id,
                        text=f"**{review_title}**: `{score}/10`",
                        parse_mode='Markdown'
                    )
                    continue

                await context.bot.send_message(
                    chat_id=user_telegram_id,
                    text=f"**{review_title}**:",
                    parse_mode='Markdown'
                )

                for item in review_data:
                    if item['text']:
                        await context.bot.send_message(
                            chat_id=user_telegram_id,
                            text=item['text']
                        )

                    if item['file_id']:
                        try:
                            file_type = item['file_type']
                            if file_type == 'photo':
                                await context.bot.send_photo(chat_id=user_telegram_id, photo=item['file_id'])
                            elif file_type == 'video':
                                await context.bot.send_video(chat_id=user_telegram_id, video=item['file_id'])
                            elif file_type == 'voice':
                                await context.bot.send_voice(chat_id=user_telegram_id, voice=item['file_id'])
                            elif file_type == 'document':
                                await context.bot.send_document(chat_id=user_telegram_id, document=item['file_id'])
                        except Exception as e:
                            print(f"خطا در ارسال فایل: {e}")
                            await context.bot.send_message(
                                chat_id=user_telegram_id,
                                text=f"⚠️ خطا در ارسال فایل"
                            )

        # دکمه بازگشت
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به آرشیو", callback_data="archive_tasks")]]
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text="━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        print(f"❌ خطا در view_archived_task_details: {e}")
        import traceback
        traceback.print_exc()

        try:
            await query.edit_message_text(
                f"❌ **خطا در نمایش جزئیات**\n\n"
                f"خطا: {str(e)}\n\n"
                f"لطفاً دوباره تلاش کنید.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[ \
                    InlineKeyboardButton("🔙 بازگشت", callback_data="archive_tasks")
                ]])
            )
        except:
            await context.bot.send_message(
                chat_id=user_telegram_id,
                text=f"❌ خطا: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[ \
                    InlineKeyboardButton("🔙 بازگشت", callback_data="archive_tasks")
                ]])
            )
    finally:
        if conn:
            conn.close()