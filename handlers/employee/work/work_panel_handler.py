# handlers/employee/work/work_panel_handler.py

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.connection import create_connection
from database.models.user import UserModel
from services.task_service import TaskService
from services.work_service import WorkService
from utils.keyboards import get_task_work_keyboard
from utils.formatters import format_time, format_time_as_hours

logger = logging.getLogger(__name__)


async def auto_refresh_work_panel(context: ContextTypes.DEFAULT_TYPE):
    """تابع برای refresh خودکار پنل کار"""
    job = context.job
    chat_id = job.chat_id
    message_id = job.data['message_id']
    task_id = job.data['task_id']
    user_id = job.data['user_id']

    logger.info(f"🔄 Auto-refreshing work panel for task_id={task_id}")

    try:
        # دریافت اطلاعات کار
        task = TaskService.get_task(task_id, with_details=True)
        if not task:
            return

        # محاسبه زمان سپری شده
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, start_time, end_time, duration_minutes, is_active
            FROM WorkSessions
            WHERE session_type = 'task' AND reference_id = ? AND user_id = ?
        """, (task_id, user_id))
        all_sessions = cursor.fetchall()

        # محاسبه زمان سپری شده به صورت دستی
        spent_time = 0
        for session in all_sessions:
            session_id, start_time, end_time, duration_minutes, is_active = session

            if end_time is None:
                # Session فعال - محاسبه زمان سپری شده تا الان
                if start_time:
                    try:
                        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                        now_dt = datetime.now()
                        elapsed = int((now_dt - start_dt).total_seconds() / 60)
                        spent_time += elapsed
                    except Exception as e:
                        logger.error(f"❌ Error in auto-refresh time calc: {e}")
            else:
                # Session تمام شده - استفاده از duration_minutes
                if duration_minutes and duration_minutes > 0:
                    spent_time += duration_minutes

        conn.close()

        allocated_time = int(task.get('duration', 0)) if task.get('duration') else 0

        # دریافت تعداد داده‌های ثبت شده
        knowledge_count = len(WorkService.get_task_knowledge(task_id, user_id))
        suggestion_count = len(WorkService.get_task_suggestions(task_id, user_id))
        results_count = len(WorkService.get_task_results(task_id, user_id))
        self_score = WorkService.get_self_score(task_id, user_id)

        # بررسی فعال بودن
        active_task_id = get_active_task_id(user_id)
        is_active = (active_task_id == task_id)

        # فرمت زمان
        spent_formatted = f"{spent_time}د"
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

        keyboard = get_task_work_keyboard(task_id, allocated_time, spent_time, is_active)

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"❌ خطا در auto-refresh: {e}")


async def show_task_work_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پنل کار با اطلاعات کامل"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    user_telegram_id = query.from_user.id

    logger.info(f"🔵 show_task_work_panel: task_id={task_id}, telegram_id={user_telegram_id}")

    # حذف job های قبلی برای این chat (فقط اگر job_queue فعال باشد)
    if context.job_queue:
        current_jobs = context.job_queue.get_jobs_by_name(f'refresh_panel_{query.message.chat_id}')
        for job in current_jobs:
            job.schedule_removal()
            logger.info(f"🗑️ Removed old refresh job")
    else:
        logger.warning("⚠️ job_queue is not available, auto-refresh will be disabled")

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

    # دریافت تمام session های این کار
    cursor.execute("""
        SELECT id, start_time, end_time, duration_minutes, is_active
        FROM WorkSessions
        WHERE session_type = 'task' AND reference_id = ? AND user_id = ?
    """, (task_id, user_id))
    all_sessions = cursor.fetchall()
    logger.info(f"🔵 Found {len(all_sessions)} WorkSessions for this task")

    # محاسبه زمان سپری شده به صورت دستی
    spent_time = 0
    for session in all_sessions:
        session_id, start_time, end_time, duration_minutes, is_active = session
        logger.info(f"   Session {session_id}: start={start_time}, end={end_time}, duration={duration_minutes}, active={is_active}")

        if end_time is None:
            # Session فعال - محاسبه زمان سپری شده تا الان
            if start_time:
                try:
                    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    now_dt = datetime.now()
                    elapsed = int((now_dt - start_dt).total_seconds() / 60)
                    logger.info(f"      ✅ Active session: {elapsed} minutes elapsed")
                    spent_time += elapsed
                except Exception as e:
                    logger.error(f"      ❌ Error calculating elapsed time: {e}")
        else:
            # Session تمام شده - استفاده از duration_minutes
            if duration_minutes and duration_minutes > 0:
                logger.info(f"      ✅ Completed session: {duration_minutes} minutes")
                spent_time += duration_minutes
            else:
                logger.warning(f"      ⚠️ Completed session has no duration!")

    logger.info(f"🔵 Total calculated spent_time: {spent_time} minutes")
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

    sent_message = await query.edit_message_text(
        message_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    # اضافه کردن job برای auto-refresh (فقط اگر کار فعال است و job_queue موجود باشد)
    if is_active and context.job_queue:
        logger.info(f"⏰ Starting auto-refresh job for task {task_id}")
        context.job_queue.run_repeating(
            auto_refresh_work_panel,
            interval=60,  # هر 60 ثانیه (1 دقیقه)
            first=60,  # اولین refresh بعد از 1 دقیقه
            chat_id=query.message.chat_id,
            name=f'refresh_panel_{query.message.chat_id}',
            data={
                'message_id': sent_message.message_id,
                'task_id': task_id,
                'user_id': user_id
            }
        )
        logger.info(f"✅ Auto-refresh job started (every 60 seconds)")
    elif is_active and not context.job_queue:
        logger.warning("⚠️ Task is active but job_queue is not available. Auto-refresh disabled.")


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