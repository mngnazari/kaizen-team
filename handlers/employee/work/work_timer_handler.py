# handlers/employee/work/work_timer_handler.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database.connection import create_connection
from database.models.user import UserModel
from database.models.work_session import WorkSessionModel
from services.task_service import TaskService
from services.time_tracking_service import TimeTrackingService

logger = logging.getLogger(__name__)


async def start_work_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تایمر کار"""
    query = update.callback_query
    await query.answer()

    logger.info(f"🔵 start_work_timer called with callback_data: {query.data}")

    task_id = int(query.data.split('_')[2])
    user_telegram_id = query.from_user.id

    logger.info(f"🔵 Parsed task_id: {task_id}, user_telegram_id: {user_telegram_id}")

    # دریافت user_id
    user = UserModel.get_by_telegram_id(user_telegram_id)
    if not user:
        logger.error(f"❌ کاربر با telegram_id={user_telegram_id} یافت نشد!")
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return

    user_id = user.get('id')
    logger.info(f"🔵 User found: user_id={user_id}")

    # بررسی اینکه روز کاری شروع شده باشد
    active_session = WorkSessionModel.get_active_session(user_id)
    logger.info(f"🔵 Active session: {active_session}")

    if not active_session:
        logger.warning(f"⚠️ کاربر {user_id} روز کاری خود را شروع نکرده است!")
        await query.answer("⚠️ ابتدا باید روز کاری خود را شروع کنید!\nاز منوی مدیریت زمان استفاده کنید.", show_alert=True)
        return

    # بررسی اینکه این کار قبلاً شروع نشده باشد
    if active_session.get('session_type') == 'task' and active_session.get('reference_id') == task_id:
        logger.info(f"ℹ️ کار {task_id} در حال حاضر در حال انجام است")
        await query.answer("⚠️ این کار در حال حاضر در حال انجام است!", show_alert=True)
        # بازگشت به پنل کار
        from .work_panel_handler import show_task_work_panel
        context.user_data['callback_query_data'] = f"work_panel_{task_id}"
        await show_task_work_panel(update, context)
        return

    # شروع کار با استفاده از TimeTrackingService
    logger.info(f"🔵 Starting task {task_id} for user {user_id}...")
    success, message = TimeTrackingService.start_task(user_id, task_id)
    logger.info(f"🔵 TimeTrackingService.start_task result: success={success}, message={message}")

    if success:
        # تغییر وضعیت کار به in_progress
        logger.info(f"🔵 Updating task {task_id} status to 'in_progress'...")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Tasks SET status = 'in_progress' WHERE id = ?
        """, (task_id,))
        conn.commit()
        conn.close()
        logger.info(f"✅ Task {task_id} status updated to 'in_progress'")

        await query.answer("✅ تایمر کار شروع شد!", show_alert=True)
    else:
        logger.error(f"❌ خطا در شروع تایمر: {message}")
        await query.answer(f"❌ {message}", show_alert=True)

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