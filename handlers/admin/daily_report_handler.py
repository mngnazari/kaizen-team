# handlers/admin/daily_report_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.user_service import UserService
from services.task_service import TaskService
from services.file_service import FileService
from services.work_service import WorkService
from services.review_service import ReviewService
from datetime import datetime, timedelta


async def show_daily_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی گزارش روزانه - نمایش لیست کارمندها با تعداد کارهای تحویلی امروز"""
    query = update.callback_query
    await query.answer()

    # Rule 3: get_all_employees() -> UserService.get_all_employees() (No change)
    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")
            ]])
        )
        return

    keyboard = []

    # تاریخ امروز
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        # Note: employees is likely a list of tuples (emp_id, telegram_id, name)
        for emp_id, telegram_id, name in employees:
            try:
                # Refactored: Use TaskService (Rule 4: SELECT COUNT(*) FROM Tasks -> TaskService مناسب)
                daily_completed = TaskService.count_daily_completed_tasks(emp_id, today)

                button_text = f"👤 {name} ({daily_completed} کار)"
                keyboard.append([
                    InlineKeyboardButton(button_text, callback_data=f"daily_report_{telegram_id}")
                ])

            except Exception as e:
                print(f"❌ خطا در دریافت گزارش {name}: {e}")
                continue

    except Exception as e:
        print(f"❌ خطای کلی در دریافت گزارش: {e}")

    # دکمه کارهای جاری
    keyboard.append([
        InlineKeyboardButton("🔄 کارهای جاری", callback_data="current_tasks")
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main_menu")
    ])

    await query.edit_message_text(
        f"📊 **گزارش روزانه**\n"
        f"📅 {datetime.now().strftime('%Y/%m/%d')}\n\n"
        f"کارمند مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_employee_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش گزارش کاری روزانه یک کارمند به تفکیک ساعات"""
    query = update.callback_query
    await query.answer()

    telegram_id = int(query.data.split('_')[2])
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        # Refactored: Use UserService (Rule 4: SELECT * FROM Users -> UserService.get_user_info())
        employee_data = UserService.get_user_info(telegram_id)

        if not employee_data:
            await query.edit_message_text("❌ کارمند یافت نشد!")
            return

        # Refactored: Use dict access (Rule 5: user tuple -> user dict)
        employee_name = employee_data.get('name')
        user_id = employee_data.get('id')

        # Refactored: Use WorkService (Rule 4)
        activities = WorkService.get_user_daily_activities(user_id, today)

        # Refactored: Use TaskService (Rule 4: SELECT COUNT(*) FROM Tasks -> TaskService مناسب)
        completed_count = TaskService.count_daily_completed_tasks(user_id, today)

    except Exception as e:
        print(f"❌ خطا در دریافت گزارش: {e}")
        await query.edit_message_text("❌ خطا در دریافت گزارش!")
        return

    if not activities:
        text = (
            f"📊 **گزارش روزانه {employee_name}**\n"
            f"📅 {datetime.now().strftime('%Y/%m/%d')}\n\n"
            f"✅ کارهای تحویل شده: {completed_count}\n\n"
            f"ℹ️ هیچ فعالیتی ثبت نشده است."
        )
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="daily_report")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    # ساخت متن گزارش
    text = (
        f"📊 **گزارش روزانه {employee_name}**\n"
        f"📅 {datetime.now().strftime('%Y/%m/%d')}\n"
        f"✅ کارهای تحویل شده: {completed_count}\n\n"
        f"⏱ **جدول زمانی کار:**\n"
        f"{'─' * 35}\n"
    )
    total_minutes = 0
    for start_time, end_time, task_title, task_duration in activities:
        try:
            # تبدیل به datetime
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                duration = end_dt - start_dt
                minutes = int(duration.total_seconds() / 60)
                total_minutes += minutes
                # ✅ محاسبه زمان کار تمام شده
                text += (
                    f"✅ {task_title}\n"
                    f"🕐 شروع: {start_dt.strftime('%H:%M')} | پایان: {end_dt.strftime('%H:%M')}\n"
                    f"⏱ مدت: {minutes} دقیقه\n"
                    f"{'─' * 35}\n"
                )
            else:
                # 🔄 کار در حال انجام
                now = datetime.now()
                elapsed = now - start_dt
                elapsed_minutes = int(elapsed.total_seconds() / 60)
                elapsed_hours = elapsed_minutes // 60
                elapsed_mins = elapsed_minutes % 60
                total_minutes += elapsed_minutes  # اضافه کردن به کل زمان امروز
                text += (
                    f"🔄 {task_title} (در حال انجام)\n"
                    f"🕐 شروع: {start_dt.strftime('%H:%M')}\n"
                    f"⏱ مدت تا کنون: {elapsed_hours}:{elapsed_mins:02d} ({elapsed_minutes} دقیقه)\n"
                    f"{'─' * 35}\n"
                )
        except Exception as e:
            print(f"خطا در محاسبه زمان: {e}")
            text += f"⚠️ خطا در محاسبه زمان برای کار {task_title}\n"

    # جمع بندی
    total_hours = total_minutes // 60
    total_mins = total_minutes % 60
    text += f"\n**جمع کل زمان کار: {total_hours}:{total_mins:02d} ({total_minutes} دقیقه)**"

    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="daily_report")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_current_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارهای در حال انجام در حال حاضر"""
    query = update.callback_query
    await query.answer()

    try:
        # Refactored: Use WorkService (Rule 4)
        current_tasks = WorkService.get_current_in_progress_tasks()

    except Exception as e:
        print(f"❌ خطا در دریافت اطلاعات: {e}")
        await query.edit_message_text("❌ خطا در دریافت اطلاعات!")
        return

    if not current_tasks:
        text = (
            "🔄 **کارهای جاری**\n\n"
            "ℹ️ در حال حاضر هیچ کاری در حال انجام نیست."
        )
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="daily_report")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    text = (
        f"🔄 **کارهای جاری**\n"
        f"📅 {datetime.now().strftime('%Y/%m/%d - %H:%M')}\n\n"
    )

    for employee_name, task_title, start_time, task_duration in current_tasks:
        try:
            # محاسبه مدت زمان کار
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            elapsed = now - start_dt
            elapsed_minutes = int(elapsed.total_seconds() / 60)

            elapsed_hours = elapsed_minutes // 60
            elapsed_mins = elapsed_minutes % 60

            # زمان تعیین شده
            duration_str = task_duration if task_duration else "تعیین نشده"

            text += (
                f"👤 **{employee_name}**\n"
                f"📋 {task_title}\n"
                f"🕐 شروع: {start_dt.strftime('%H:%M')}\n"
                f"⏱ مدت تا کنون: {elapsed_hours}:{elapsed_mins:02d} ({elapsed_minutes} دقیقه)\n"
                f"📅 زمان برنامه‌ریزی شده: {duration_str}\n"
                f"{'─' * 35}\n\n"
            )
        except Exception as e:
            print(f"خطا در پردازش کار: {e}")
            continue

    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="daily_report")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )