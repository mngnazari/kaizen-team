# handlers/employee/time_tracking_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.time_tracking_service import TimeTrackingService
from services.task_service import TaskService
from database.models.daily_activity import DailyActivityModel


async def show_time_tracking_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی مدیریت زمان برای کارمند"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # دریافت وضعیت فعلی
    status = TimeTrackingService.get_current_status(user_id)

    keyboard = []

    if not status['is_working']:
        # هنوز روز کاری شروع نشده
        keyboard.append([InlineKeyboardButton("▶️ شروع روز کاری", callback_data="start_work_day")])
    else:
        # روز کاری شروع شده
        keyboard.append([InlineKeyboardButton("⏹ پایان روز کاری", callback_data="end_work_day")])
        keyboard.append([InlineKeyboardButton("⏱ وضعیت فعلی", callback_data="current_status")])
        keyboard.append([InlineKeyboardButton("🔄 تغییر فعالیت", callback_data="change_activity")])

    keyboard.append([InlineKeyboardButton("📊 گزارش امروز", callback_data="today_report")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu_employee")])

    message = "⏱ **مدیریت زمان کاری**\n\n"
    if status['is_working']:
        message += f"✅ روز کاری شما فعال است.\n\n{status.get('message', '')}"
    else:
        message += "لطفاً روز کاری خود را شروع کنید."

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def start_work_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع روز کاری"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    success, message = TimeTrackingService.start_work_day(user_id)

    if success:
        await query.edit_message_text(
            f"✅ {message}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📋 انتخاب کار", callback_data="select_task"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
            ]]),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            f"❌ {message}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
            ]]),
            parse_mode='Markdown'
        )


async def end_work_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پایان روز کاری"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    success, message = TimeTrackingService.end_work_day(user_id)

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
        ]]),
        parse_mode='Markdown'
    )


async def show_current_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش وضعیت فعلی تایمر"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    status = TimeTrackingService.get_current_status(user_id)

    if not status['is_working']:
        await query.edit_message_text(
            "❌ شما هنوز روز کاری را شروع نکرده‌اید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
            ]])
        )
        return

    await query.edit_message_text(
        f"⏱ **وضعیت فعلی**\n\n{status.get('message', '')}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 تغییر فعالیت", callback_data="change_activity"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
        ]]),
        parse_mode='Markdown'
    )


async def show_change_activity_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی تغییر فعالیت"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📋 انتخاب کار", callback_data="select_task")],
        [InlineKeyboardButton("🍽 نهار و نماز", callback_data="activity_lunch_prayer")],
        [InlineKeyboardButton("☕ استراحت", callback_data="activity_break")],
        [InlineKeyboardButton("⏸ بیکاری", callback_data="activity_idle")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")]
    ]

    await query.edit_message_text(
        "🔄 **انتخاب فعالیت**\n\n"
        "لطفاً فعالیت بعدی خود را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def select_task_for_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کار برای شروع تایمر"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # دریافت کارهای کارمند
    tasks = TaskService.get_employee_tasks(user_id, status='in_progress')
    if not tasks:
        tasks = TaskService.get_employee_tasks(user_id, status='pending')

    if not tasks:
        await query.edit_message_text(
            "❌ شما هیچ کاری برای انجام ندارید!\n\n"
            "لطفاً با مدیر خود تماس بگیرید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="change_activity")
            ]])
        )
        return

    keyboard = []
    for task in tasks:
        task_id = task.get('id')
        title = task.get('title')
        status_emoji = '⏳' if task.get('status') == 'pending' else '🔄'
        keyboard.append([
            InlineKeyboardButton(f"{status_emoji} {title}", callback_data=f"start_timer_{task_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="change_activity")])

    await query.edit_message_text(
        "📋 **انتخاب کار**\n\n"
        "لطفاً کاری را که می‌خواهید روی آن کار کنید انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def start_task_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تایمر روی یک کار"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    task_id = int(query.data.split('_')[2])

    success, message = TimeTrackingService.start_task(user_id, task_id)

    if success:
        await query.edit_message_text(
            f"✅ {message}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⏱ وضعیت فعلی", callback_data="current_status"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
            ]]),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            f"❌ {message}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="select_task")
            ]]),
            parse_mode='Markdown'
        )


async def start_daily_activity_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تایمر برای فعالیت روزانه"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    activity_key = query.data.split('_')[1]  # lunch_prayer, break, idle

    # برای استراحت، نمایش کارهای تمام نشده
    if activity_key == 'break':
        unfinished_tasks = TimeTrackingService.get_unfinished_tasks_during_break(user_id)
        context.user_data['break_unfinished_tasks'] = unfinished_tasks

    success, message = TimeTrackingService.start_daily_activity(user_id, activity_key)

    keyboard = [[
        InlineKeyboardButton("⏱ وضعیت فعلی", callback_data="current_status"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
    ]]

    # برای استراحت، اگر کارهای تمام نشده وجود دارد
    if activity_key == 'break' and success and context.user_data.get('break_unfinished_tasks'):
        unfinished_tasks = context.user_data['break_unfinished_tasks']
        if unfinished_tasks:
            importance_map = {1: '🔴', 2: '🟡', 3: '🟢'}
            priority_map = {1: '⚡', 2: '⚡', 3: '▪️'}

            tasks_text = "\n\n⚠️ **کارهای محول شده (تمام نشده):**\n"
            for task in unfinished_tasks[:5]:  # نمایش 5 کار اول
                imp_emoji = importance_map.get(task.get('importance'), '❓')
                pri_emoji = priority_map.get(task.get('priority'), '▪️')
                tasks_text += f"\n{imp_emoji}{pri_emoji} {task.get('title')}"

            message += tasks_text

    await query.edit_message_text(
        f"✅ {message}" if success else f"❌ {message}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_today_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش گزارش امروز"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    summary = TimeTrackingService.get_today_summary(user_id)

    if summary.get('total_time', 0) == 0:
        await query.edit_message_text(
            "📊 **گزارش امروز**\n\n"
            "هنوز فعالیتی ثبت نشده است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
            ]]),
            parse_mode='Markdown'
        )
        return

    total_hours = summary.get('total_time', 0) // 60
    total_mins = summary.get('total_time', 0) % 60

    task_hours = summary.get('task_time', 0) // 60
    task_mins = summary.get('task_time', 0) % 60

    report_text = (
        f"📊 **گزارش امروز** ({summary.get('date')})\n\n"
        f"⏱ **کار روی تسک‌ها:** {task_hours}h {task_mins}m\n"
        f"🍽 **نهار و نماز:** {summary.get('lunch_time', 0)} دقیقه\n"
        f"☕ **استراحت:** {summary.get('break_time', 0)} دقیقه\n"
        f"⏸ **بیکاری:** {summary.get('idle_time', 0)} دقیقه\n\n"
        f"📈 **جمع کل:** {total_hours}h {total_mins}m"
    )

    await query.edit_message_text(
        report_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="time_tracking_menu")
        ]]),
        parse_mode='Markdown'
    )
