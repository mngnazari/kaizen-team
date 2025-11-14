# handlers/employee/employee_task_handler.py

import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, CommandHandler

from database.connection import create_connection
from services.user_service import UserService
from services.task_service import TaskService

# --- وضعیت‌های مکالمه ---
TASK_START_CONFIRMATION, TASK_WORK_VIEW = range(10, 12)

tasks_in_progress = {}


def get_employee_main_keyboard():
    """کیبورد اصلی مخصوص نیروها"""
    keyboard = [
        [InlineKeyboardButton("📝 کارها", callback_data="list_tasks")],
        [InlineKeyboardButton("🗂 آرشیو کارها", callback_data="archive_tasks")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_active_task_id(user_db_id):
    """یافتن کار فعال کاربر"""
    conn = create_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT reference_id FROM WorkSessions
            WHERE user_id = ? AND session_type = 'task' AND is_active = 1
            LIMIT 1
        """, (user_db_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()


async def back_to_tasks_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به فهرست کارها"""
    query = update.callback_query
    await query.answer()
    await list_employee_tasks(update, context)
    return ConversationHandler.END


async def cancel_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو مکالمه شروع کار"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ شروع کار لغو شد.")
    await list_employee_tasks(update, context)
    return ConversationHandler.END


async def list_employee_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارهای اختصاص داده شده به نیرو"""
    query = update.callback_query
    await query.answer()

    user_telegram_id = query.from_user.id

    conn = create_connection()
    if not conn:
        await query.edit_message_text("❌ خطا در اتصال به دیتابیس!")
        return

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (user_telegram_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    user_db_id = result[0]

    # فقط کارهای pending و in_progress
    cursor.execute("""
        SELECT id, title, status FROM Tasks 
        WHERE assigned_to_id = ? AND status IN ('pending', 'in_progress')
        ORDER BY status DESC
    """, (user_db_id,))
    tasks = cursor.fetchall()

    # دریافت کار فعال
    active_task_id = get_active_task_id(user_db_id)

    conn.close()

    if not tasks:
        await query.edit_message_text("📭 هیچ کار فعالی به شما محول نشده است.")
        return

    keyboard = []
    for task_id, task_title, status in tasks:
        if task_id == active_task_id:
            title_display = f"🟢 {task_title}"
        else:
            title_display = f"📌 {task_title}"

        row = [
            InlineKeyboardButton("📋 شناسنامه", callback_data=f"details_{task_id}"),
            InlineKeyboardButton(title_display, callback_data=f"work_panel_{task_id}")
        ]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🗂 آرشیو کارها", callback_data="archive_tasks")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu_employee")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📝 لیست کارهای محول‌شده به شما:", reply_markup=reply_markup)


async def view_task_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش شناسنامه کامل کار با تمام جزئیات و فایل‌ها به ترتیب"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[1])
    user_telegram_id = query.from_user.id

    conn = create_connection()
    if not conn:
        await query.edit_message_text("❌ خطا در اتصال به دیتابیس!")
        return

    cursor = conn.cursor()

    # دریافت اطلاعات کامل کار
    cursor.execute("""
        SELECT t.title, t.description, t.duration, t.results, t.importance, 
               t.priority, t.creation_date, c.name as category_name
        FROM Tasks t
        LEFT JOIN Categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (task_id,))
    task_info = cursor.fetchone()

    if not task_info:
        conn.close()
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    title, description, duration, results, importance, priority, creation_date, category_name = task_info

    # 🔍 دیباگ: چک کردن فایل‌های بخش توضیحات
    cursor.execute("""
        SELECT file_id, file_type FROM TaskSectionFiles 
        WHERE task_id = ? AND section_type = 'description'
    """, (task_id,))
    description_files = cursor.fetchall()
    print(f"🔍 DEBUG: تعداد فایل‌های توضیحات = {len(description_files)}")
    print(f"🔍 DEBUG: فایل‌های توضیحات = {description_files}")

    # 🔍 دیباگ: چک کردن فایل‌های بخش نتایج
    cursor.execute("""
        SELECT file_id, file_type FROM TaskSectionFiles 
        WHERE task_id = ? AND section_type = 'results'
    """, (task_id,))
    results_files = cursor.fetchall()
    print(f"🔍 DEBUG: تعداد فایل‌های نتایج = {len(results_files)}")
    print(f"🔍 DEBUG: فایل‌های نتایج = {results_files}")

    # 🔍 دیباگ: چک کردن تمام فایل‌ها
    cursor.execute("SELECT * FROM TaskSectionFiles WHERE task_id = ?", (task_id,))
    all_files = cursor.fetchall()
    print(f"🔍 DEBUG: تمام فایل‌های task_id={task_id}: {all_files}")

    conn.close()

    # ========== ارسال شناسنامه خلاصه ==========
    summary_text = (
        f"📋 **شناسنامه کار**\n\n"
        f"**📌 عنوان:** {title}\n"
        f"**📂 دسته‌بندی:** {category_name or 'ندارد'}\n"
        f"**⏱ مدت زمان:** {duration or 'تعیین نشده'} دقیقه\n"
        f"**⭐ اهمیت:** {importance or 'ندارد'}\n"
        f"**🔥 اولویت:** {priority or 'ندارد'}\n"
        f"**📅 تاریخ ایجاد:** {creation_date}\n"
    )

    await query.edit_message_text(summary_text, parse_mode='Markdown')

    # ========== 1. توضیحات ==========
    if description or description_files:
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📝 **توضیحات کار**",
            parse_mode='Markdown'
        )

        # متن توضیحات
        if description:
            await context.bot.send_message(
                chat_id=user_telegram_id,
                text=description
            )

        # فایل‌های توضیحات
        if description_files:
            for file_id, file_type in description_files:
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
        else:
            print("⚠️ هیچ فایلی در بخش توضیحات یافت نشد!")
    else:
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📝 **توضیحات کار**\n\nتوضیحاتی ثبت نشده است.",
            parse_mode='Markdown'
        )

    # ========== 2. نتایج مورد انتظار ==========
    if results or results_files:
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📊 **نتایج مورد انتظار**",
            parse_mode='Markdown'
        )

        # متن نتایج
        if results:
            await context.bot.send_message(
                chat_id=user_telegram_id,
                text=results
            )

        # فایل‌های نتایج
        if results_files:
            for file_id, file_type in results_files:
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
        else:
            print("⚠️ هیچ فایلی در بخش نتایج یافت نشد!")
    else:
        await context.bot.send_message(
            chat_id=user_telegram_id,
            text="━━━━━━━━━━━━━━━━━\n📊 **نتایج مورد انتظار**\n\nنتایجی ثبت نشده است.",
            parse_mode='Markdown'
        )

    # ========== دکمه بازگشت ==========
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به کارها", callback_data="list_tasks")]]
    await context.bot.send_message(
        chat_id=user_telegram_id,
        text="━━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def employee_fallback_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ عملیات لغو شد.")
    else:
        await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END


employee_conv_handler = ConversationHandler(
    entry_points=[],
    states={
        TASK_START_CONFIRMATION: [
            CallbackQueryHandler(cancel_task_start, pattern='^cancel_start_task$')
        ],
        TASK_WORK_VIEW: []
    },
    fallbacks=[
        CommandHandler("cancel", employee_fallback_cancel),
        CallbackQueryHandler(employee_fallback_cancel, pattern='^cancel_employee$')
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)
