# handlers/employee/work/work_panel_handler.py

import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.connection import create_connection
from database.models.user import UserModel
from services.task_service import TaskService
from services.work_service import WorkService
from utils.keyboards import get_task_work_keyboard
from utils.formatters import format_time, format_time_as_hours

logger = logging.getLogger(__name__)


async def show_task_work_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پنل کار با اطلاعات کامل"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    user_telegram_id = query.from_user.id

    logger.info(f"🔵 show_task_work_panel: task_id={task_id}, telegram_id={user_telegram_id}")

    # دریافت اطلاعات کاربر
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        logger.error(f"❌ کاربر با telegram_id={user_telegram_id} یافت نشد!")
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    user_id = user.get('id')
    logger.info(f"🔵 User found: user_id={user_id}")

    # دریافت اطلاعات کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # دریافت زمان سپری شده از WorkSessions
    logger.info(f"🔵 Calculating spent time for task_id={task_id}, user_id={user_id}")
    conn = create_connection()
    cursor = conn.cursor()

    # ابتدا ببینیم چند WorkSession برای این کار وجود دارد
    cursor.execute("""
        SELECT id, start_time, end_time, duration_minutes, is_active
        FROM WorkSessions
        WHERE session_type = 'task' AND reference_id = ? AND user_id = ?
    """, (task_id, user_id))
    all_sessions = cursor.fetchall()
    logger.info(f"🔵 Found {len(all_sessions)} WorkSessions for this task")
    for session in all_sessions:
        logger.info(f"   Session {session[0]}: start={session[1]}, end={session[2]}, duration={session[3]}, active={session[4]}")

    cursor.execute("""
        SELECT COALESCE(SUM(
            CASE
                WHEN end_time IS NULL THEN
                    CAST((JULIANDAY(datetime('now')) - JULIANDAY(start_time)) * 24 * 60 AS INTEGER)
                ELSE
                    duration_minutes
            END
        ), 0) as total_minutes
        FROM WorkSessions
        WHERE session_type = 'task' AND reference_id = ? AND user_id = ?
    """, (task_id, user_id))
    result = cursor.fetchone()
    spent_time = result[0] if result and result[0] is not None and result[0] >= 0 else 0
    logger.info(f"🔵 Calculated spent_time: {spent_time} minutes")
    conn.close()

    # محاسبه زمان تخصیصی (به دقیقه)
    allocated_time = int(task.get('duration', 0)) if task.get('duration') else 0

    # دریافت تعداد داده‌های ثبت شده
    knowledge_count = len(WorkService.get_task_knowledge(task_id, user_id))
    suggestion_count = len(WorkService.get_task_suggestions(task_id, user_id))
    results_count = len(WorkService.get_task_results(task_id, user_id))
    self_score = WorkService.get_self_score(task_id, user_id)

    # بررسی آیا این کار در حال انجام است
    active_task_id = get_active_task_id(user_id)
    is_active = (active_task_id == task_id)

    # ساخت متن پنل
    spent_formatted = f"{spent_time}د"  # زمان سپری شده به دقیقه
    allocated_formatted = format_time(allocated_time) if allocated_time > 0 else "تعیین نشده"

    message_text = (
        f"📋 **{task.get('title')}**\n\n"
        f"⏱️ زمان کل: {allocated_formatted}\n"
        f"⌚ زمان سپری شده: {spent_formatted}\n\n"
        f"📊 **وضعیت ثبت داده‌ها:**\n"
        f"📚 دانش: {knowledge_count}\n"
        f"💡 پیشنهاد: {suggestion_count}\n"
        f"📋 نتایج: {results_count}\n"
        f"⭐ امتیاز خود: {'✅ ثبت شده' if self_score else '❌ ثبت نشده'}\n"
    )

    # دریافت کیبورد
    keyboard = get_task_work_keyboard(task_id, allocated_time, spent_time, is_active)

    await query.edit_message_text(
        message_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


def get_active_task_id(user_id: int) -> int:
    """دریافت task_id کار فعال کاربر"""
    conn = create_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT reference_id FROM WorkSessions
            WHERE user_id = ? AND session_type = 'task' AND is_active = 1
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()