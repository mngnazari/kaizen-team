# handlers/admin/time_reports_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.user_service import UserService
from services.time_tracking_service import TimeTrackingService
from database.models.work_session import WorkSessionModel
from datetime import datetime, timedelta


async def show_time_reports_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی گزارشات زمان"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📊 گزارش امروز", callback_data="time_report_today")],
        [InlineKeyboardButton("📅 گزارش هفته جاری", callback_data="time_report_week")],
        [InlineKeyboardButton("👥 گزارش کارمندان", callback_data="time_report_employees")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")]
    ]

    await query.edit_message_text(
        "📊 **گزارشات زمان**\n\n"
        "لطفاً نوع گزارش را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_today_time_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """گزارش زمان امروز همه کارمندان"""
    query = update.callback_query
    await query.answer()

    today = datetime.now().strftime("%Y-%m-%d")
    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_reports")
            ]])
        )
        return

    report_text = f"📊 **گزارش زمان امروز** ({today})\n\n"

    total_task_time = 0
    total_idle_time = 0
    total_break_time = 0

    for emp in employees:
        user_id = emp.get('user_id')
        full_name = emp.get('full_name')

        # دریافت خلاصه امروز
        summary = WorkSessionModel.get_daily_summary(user_id, today)

        if summary.get('total_time', 0) > 0:
            task_time = summary.get('task_time', 0)
            lunch_time = summary.get('lunch_time', 0)
            break_time = summary.get('break_time', 0)
            idle_time = summary.get('idle_time', 0)

            total_task_time += task_time
            total_idle_time += idle_time
            total_break_time += break_time

            # محاسبه ساعت و دقیقه
            task_h = task_time // 60
            task_m = task_time % 60

            report_text += (
                f"👤 **{full_name}**\n"
                f"   📋 کار: {task_h}h {task_m}m\n"
                f"   🍽 نهار: {lunch_time}m\n"
                f"   ☕ استراحت: {break_time}m\n"
                f"   ⏸ بیکاری: {idle_time}m\n\n"
            )
        else:
            report_text += f"👤 **{full_name}**: فعالیتی ثبت نشده\n\n"

    # خلاصه کل
    total_task_h = total_task_time // 60
    total_task_m = total_task_time % 60

    report_text += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 **جمع کل کار روی تسک‌ها:** {total_task_h}h {total_task_m}m\n"
        f"☕ **جمع استراحت:** {total_break_time}m\n"
        f"⏸ **جمع بیکاری:** {total_idle_time}m"
    )

    await query.edit_message_text(
        report_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="time_reports")
        ]]),
        parse_mode='Markdown'
    )


async def show_week_time_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """گزارش زمان هفته جاری"""
    query = update.callback_query
    await query.answer()

    # محاسبه تاریخ‌های هفته
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())

    week_dates = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        week_dates.append(date.strftime("%Y-%m-%d"))

    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_reports")
            ]])
        )
        return

    report_text = f"📅 **گزارش هفته جاری**\n\n"

    for emp in employees:
        user_id = emp.get('user_id')
        full_name = emp.get('full_name')

        week_task_time = 0
        week_break_time = 0
        week_idle_time = 0
        work_days = 0

        for date in week_dates:
            summary = WorkSessionModel.get_daily_summary(user_id, date)
            if summary.get('total_time', 0) > 0:
                week_task_time += summary.get('task_time', 0)
                week_break_time += summary.get('break_time', 0)
                week_idle_time += summary.get('idle_time', 0)
                work_days += 1

        if week_task_time > 0 or work_days > 0:
            task_h = week_task_time // 60
            task_m = week_task_time % 60

            report_text += (
                f"👤 **{full_name}**\n"
                f"   📋 کار: {task_h}h {task_m}m ({work_days} روز)\n"
                f"   ☕ استراحت: {week_break_time}m\n"
                f"   ⏸ بیکاری: {week_idle_time}m\n\n"
            )
        else:
            report_text += f"👤 **{full_name}**: فعالیتی ثبت نشده\n\n"

    await query.edit_message_text(
        report_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="time_reports")
        ]]),
        parse_mode='Markdown'
    )


async def show_employees_time_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کارمند برای گزارش تفصیلی"""
    query = update.callback_query
    await query.answer()

    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_reports")
            ]])
        )
        return

    keyboard = []
    for emp in employees:
        user_id = emp.get('user_id')
        full_name = emp.get('full_name')

        keyboard.append([
            InlineKeyboardButton(
                f"👤 {full_name}",
                callback_data=f"emp_time_report_{user_id}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="time_reports")])

    await query.edit_message_text(
        "👥 **گزارش کارمندان**\n\n"
        "کارمند مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_employee_detailed_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """گزارش تفصیلی یک کارمند"""
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[3])

    employee = UserService.get_employee_by_user_id(user_id)
    if not employee:
        await query.edit_message_text(
            "❌ کارمند یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_report_employees")
            ]])
        )
        return

    # گزارش 7 روز اخیر
    report_text = f"👤 **گزارش تفصیلی: {employee['full_name']}**\n\n"

    today = datetime.now()
    total_task_time = 0
    total_break_time = 0
    total_idle_time = 0

    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        summary = WorkSessionModel.get_daily_summary(user_id, date)

        if summary.get('total_time', 0) > 0:
            task_time = summary.get('task_time', 0)
            lunch_time = summary.get('lunch_time', 0)
            break_time = summary.get('break_time', 0)
            idle_time = summary.get('idle_time', 0)

            total_task_time += task_time
            total_break_time += break_time
            total_idle_time += idle_time

            task_h = task_time // 60
            task_m = task_time % 60

            # دریافت کارهای تمام نشده در روز استراحت
            unfinished_indicator = ""
            if break_time > 0:
                # نمایش اینکه در این روز استراحت داشته
                unfinished_tasks = TimeTrackingService.get_unfinished_tasks_during_break(user_id)
                if unfinished_tasks:
                    unfinished_indicator = " ⚠️"

            report_text += (
                f"📅 **{date}**{unfinished_indicator}\n"
                f"   📋 کار: {task_h}h {task_m}m\n"
                f"   🍽 نهار: {lunch_time}m | ☕ استراحت: {break_time}m | ⏸ بیکاری: {idle_time}m\n\n"
            )
        else:
            report_text += f"📅 **{date}**: فعالیتی ثبت نشده\n\n"

    # خلاصه کل
    total_h = total_task_time // 60
    total_m = total_task_time % 60

    report_text += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 **جمع کل (7 روز):**\n"
        f"   📋 کار: {total_h}h {total_m}m\n"
        f"   ☕ استراحت: {total_break_time}m\n"
        f"   ⏸ بیکاری: {total_idle_time}m\n\n"
        f"⚠️ = کارهای تمام نشده در زمان استراحت"
    )

    keyboard = [
        [InlineKeyboardButton("📊 جزئیات بیشتر", callback_data=f"detailed_break_{user_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="time_report_employees")]
    ]

    await query.edit_message_text(
        report_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_detailed_break_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش جزئیات کارهای تمام نشده در زمان استراحت"""
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[2])

    employee = UserService.get_employee_by_user_id(user_id)
    if not employee:
        await query.answer("❌ کارمند یافت نشد!", show_alert=True)
        return

    # دریافت کارهای تمام نشده
    unfinished_tasks = TimeTrackingService.get_unfinished_tasks_during_break(user_id)

    if not unfinished_tasks:
        await query.answer("✅ همه کارها تحویل شده‌اند!", show_alert=True)
        return

    importance_map = {1: '🔴', 2: '🟡', 3: '🟢'}
    priority_map = {1: '⚡⚡', 2: '⚡', 3: '▪️'}

    report_text = (
        f"⚠️ **کارهای تمام نشده**\n"
        f"👤 کارمند: {employee['full_name']}\n\n"
    )

    for task in unfinished_tasks:
        imp_emoji = importance_map.get(task.get('importance'), '❓')
        pri_emoji = priority_map.get(task.get('priority'), '▪️')
        title = task.get('title')
        category = task.get('category_name', 'بدون دسته')

        report_text += f"{imp_emoji}{pri_emoji} **{title}**\n"
        report_text += f"   📁 {category}\n\n"

    report_text += (
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔴 = اهمیت بالا | 🟡 = اهمیت متوسط | 🟢 = اهمیت کم\n"
        f"⚡⚡ = اولویت بالا | ⚡ = اولویت متوسط"
    )

    await query.edit_message_text(
        report_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data=f"emp_time_report_{user_id}")
        ]]),
        parse_mode='Markdown'
    )
