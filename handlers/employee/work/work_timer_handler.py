# handlers/employee/work/work_timer_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database.connection import create_connection
from database.models.user import UserModel
from services.task_service import TaskService


async def start_work_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تایمر کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    user_telegram_id = query.from_user.id

    # دریافت user_id
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    user_id = user.get('id')

    # بررسی وجود کار فعال
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT task_id FROM TaskActivities 
        WHERE user_id = ? AND end_time IS NULL
    """, (user_id,))
    active_task = cursor.fetchone()

    if active_task:
        await query.answer("⚠️ شما در حال حاضر یک کار فعال دارید!", show_alert=True)
        conn.close()
        return

    # شروع تایمر جدید
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO TaskActivities (user_id, task_id, start_time)
        VALUES (?, ?, ?)
    """, (user_id, task_id, start_time))

    # تغییر وضعیت کار به in_progress
    cursor.execute("""
        UPDATE Tasks SET status = 'in_progress' WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    await query.answer("✅ تایمر کار شروع شد!", show_alert=True)

    # بازگشت به پنل کار
    from .work_panel_handler import show_task_work_panel
    context.user_data['callback_query_data'] = f"work_panel_{task_id}"
    await show_task_work_panel(update, context)


async def end_work_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پایان تایمر کار"""
    query = update.callback_query
    await query.answer()

    user_telegram_id = query.from_user.id

    # دریافت user_id
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    user_id = user.get('id')

    # پایان تایمر
    conn = create_connection()
    cursor = conn.cursor()

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE TaskActivities 
        SET end_time = ?
        WHERE user_id = ? AND end_time IS NULL
    """, (end_time, user_id))

    conn.commit()
    conn.close()

    await query.answer("✅ تایمر متوقف شد!", show_alert=True)