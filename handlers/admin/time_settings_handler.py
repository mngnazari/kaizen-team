# handlers/admin/time_settings_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from database.models.work_schedule import WorkScheduleModel
from database.models.holiday import HolidayModel
from services.user_service import UserService

# States for conversation
GET_START_TIME, GET_END_TIME, GET_HOLIDAY_DATE, GET_HOLIDAY_TITLE = range(4)


async def show_time_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی تنظیمات زمان و تعطیلات"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏰ تنظیم ساعات کاری", callback_data="set_work_hours")],
        [InlineKeyboardButton("📅 مدیریت تعطیلات", callback_data="manage_holidays")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")]
    ]

    await query.edit_message_text(
        "⚙️ **تنظیمات زمان**\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_work_hours_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی تنظیم ساعات کاری کارمندان"""
    query = update.callback_query
    await query.answer()

    # دریافت لیست کارمندان
    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="time_settings")
            ]])
        )
        return

    keyboard = []
    for emp in employees:
        user_id = emp.get('user_id')
        full_name = emp.get('full_name')

        # دریافت ساعت کاری فعلی
        schedule = WorkScheduleModel.get_by_user_id(user_id)
        if schedule:
            time_info = f"{schedule['start_time']} - {schedule['end_time']}"
        else:
            time_info = "تنظیم نشده"

        keyboard.append([
            InlineKeyboardButton(
                f"👤 {full_name} ({time_info})",
                callback_data=f"edit_schedule_{user_id}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="time_settings")])

    await query.edit_message_text(
        "⏰ **تنظیم ساعات کاری**\n\n"
        "کارمند مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def start_edit_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ویرایش ساعت کاری کارمند"""
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[2])
    context.user_data['schedule_user_id'] = user_id

    # دریافت اطلاعات کارمند
    employee = UserService.get_employee_by_user_id(user_id)
    if not employee:
        await query.edit_message_text(
            "❌ کارمند یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="set_work_hours")
            ]])
        )
        return

    # دریافت ساعت کاری فعلی
    schedule = WorkScheduleModel.get_by_user_id(user_id)
    current_schedule = ""
    if schedule:
        current_schedule = f"\n📌 **ساعت کاری فعلی:** {schedule['start_time']} - {schedule['end_time']}"

    await query.edit_message_text(
        f"⏰ **تنظیم ساعت کاری**\n\n"
        f"👤 کارمند: {employee['full_name']}{current_schedule}\n\n"
        f"لطفاً ساعت شروع کار را وارد کنید (مثال: 10:00):",
        parse_mode='Markdown'
    )

    return GET_START_TIME


async def get_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت ساعت شروع کار"""
    start_time = update.message.text.strip()

    # اعتبارسنجی فرمت ساعت
    if not _validate_time_format(start_time):
        await update.message.reply_text(
            "❌ فرمت ساعت نادرست است!\n"
            "لطفاً به فرمت HH:MM وارد کنید (مثال: 10:00):"
        )
        return GET_START_TIME

    context.user_data['start_time'] = start_time

    await update.message.reply_text(
        f"✅ ساعت شروع: {start_time}\n\n"
        f"حالا ساعت پایان کار را وارد کنید (مثال: 19:00):"
    )

    return GET_END_TIME


async def get_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت ساعت پایان کار و ذخیره"""
    end_time = update.message.text.strip()

    # اعتبارسنجی فرمت ساعت
    if not _validate_time_format(end_time):
        await update.message.reply_text(
            "❌ فرمت ساعت نادرست است!\n"
            "لطفاً به فرمت HH:MM وارد کنید (مثال: 19:00):"
        )
        return GET_END_TIME

    user_id = context.user_data['schedule_user_id']
    start_time = context.user_data['start_time']

    # ذخیره ساعت کاری
    success = WorkScheduleModel.update(user_id, start_time, end_time)

    if success:
        employee = UserService.get_employee_by_user_id(user_id)
        await update.message.reply_text(
            f"✅ ساعت کاری برای {employee['full_name']} با موفقیت ثبت شد!\n\n"
            f"🕐 شروع: {start_time}\n"
            f"🕔 پایان: {end_time}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="set_work_hours")
            ]]),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ خطا در ثبت ساعت کاری!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="set_work_hours")
            ]])
        )

    return ConversationHandler.END


async def show_holidays_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی مدیریت تعطیلات"""
    query = update.callback_query
    await query.answer()

    # دریافت تعطیلات مناسبتی
    holidays = HolidayModel.get_occasional_holidays()

    keyboard = [
        [InlineKeyboardButton("➕ افزودن تعطیلی جدید", callback_data="add_holiday")]
    ]

    if holidays:
        keyboard.append([InlineKeyboardButton("📋 لیست تعطیلات", callback_data="list_holidays")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="time_settings")])

    holidays_text = ""
    if holidays:
        holidays_text = "\n\n📅 **تعطیلات ثبت شده:**\n"
        for holiday in holidays[:5]:  # نمایش 5 تعطیلی اخیر
            holidays_text += f"▪️ {holiday['holiday_date']}: {holiday['title']}\n"

    await query.edit_message_text(
        f"📅 **مدیریت تعطیلات**{holidays_text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def start_add_holiday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع افزودن تعطیلی جدید"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📅 **افزودن تعطیلی جدید**\n\n"
        "لطفاً تاریخ تعطیلی را به فرمت YYYY-MM-DD وارد کنید:\n"
        "(مثال: 2025-03-20)",
        parse_mode='Markdown'
    )

    return GET_HOLIDAY_DATE


async def get_holiday_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت تاریخ تعطیلی"""
    date_str = update.message.text.strip()

    # اعتبارسنجی فرمت تاریخ
    if not _validate_date_format(date_str):
        await update.message.reply_text(
            "❌ فرمت تاریخ نادرست است!\n"
            "لطفاً به فرمت YYYY-MM-DD وارد کنید (مثال: 2025-03-20):"
        )
        return GET_HOLIDAY_DATE

    context.user_data['holiday_date'] = date_str

    await update.message.reply_text(
        f"✅ تاریخ: {date_str}\n\n"
        f"حالا عنوان تعطیلی را وارد کنید:"
    )

    return GET_HOLIDAY_TITLE


async def get_holiday_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت عنوان تعطیلی و ذخیره"""
    title = update.message.text.strip()

    if not title:
        await update.message.reply_text(
            "❌ عنوان نمی‌تواند خالی باشد!\n"
            "لطفاً عنوان تعطیلی را وارد کنید:"
        )
        return GET_HOLIDAY_TITLE

    date_str = context.user_data['holiday_date']

    # ذخیره تعطیلی
    holiday_id = HolidayModel.create(date_str, title, 'occasional')

    if holiday_id:
        await update.message.reply_text(
            f"✅ تعطیلی با موفقیت ثبت شد!\n\n"
            f"📅 تاریخ: {date_str}\n"
            f"📝 عنوان: {title}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_holidays")
            ]])
        )
    else:
        await update.message.reply_text(
            "❌ خطا در ثبت تعطیلی! (احتمالاً این تاریخ قبلاً ثبت شده است)",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_holidays")
            ]])
        )

    return ConversationHandler.END


async def show_holidays_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کامل تعطیلات"""
    query = update.callback_query
    await query.answer()

    holidays = HolidayModel.get_occasional_holidays()

    if not holidays:
        await query.edit_message_text(
            "📅 هیچ تعطیلی ثبت نشده است!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_holidays")
            ]])
        )
        return

    keyboard = []
    for holiday in holidays:
        holiday_id = holiday.get('id')
        date = holiday.get('holiday_date')
        title = holiday.get('title')

        keyboard.append([
            InlineKeyboardButton(
                f"📅 {date}: {title}",
                callback_data=f"delete_holiday_{holiday_id}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage_holidays")])

    await query.edit_message_text(
        "📋 **لیست تعطیلات**\n\n"
        "برای حذف، روی تعطیلی مورد نظر کلیک کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def delete_holiday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف تعطیلی"""
    query = update.callback_query
    await query.answer()

    holiday_id = int(query.data.split('_')[2])

    success = HolidayModel.delete(holiday_id)

    if success:
        await query.answer("✅ تعطیلی حذف شد!", show_alert=True)
    else:
        await query.answer("❌ خطا در حذف تعطیلی!", show_alert=True)

    # بازگشت به لیست
    await show_holidays_list(update, context)


async def cancel_time_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    await update.message.reply_text(
        "❌ عملیات لغو شد.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت", callback_data="time_settings")
        ]])
    )
    return ConversationHandler.END


def _validate_time_format(time_str: str) -> bool:
    """اعتبارسنجی فرمت ساعت HH:MM"""
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            return False
        hour, minute = int(parts[0]), int(parts[1])
        return 0 <= hour < 24 and 0 <= minute < 60
    except:
        return False


def _validate_date_format(date_str: str) -> bool:
    """اعتبارسنجی فرمت تاریخ YYYY-MM-DD"""
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False


# ========== ConversationHandler برای تنظیم ساعات کاری ==========
schedule_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_edit_schedule, pattern='^edit_schedule_')],
    states={
        GET_START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_start_time)],
        GET_END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_end_time)],
    },
    fallbacks=[MessageHandler(filters.Regex('^لغو$'), cancel_time_settings)],
)

# ========== ConversationHandler برای افزودن تعطیلی ==========
holiday_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_holiday, pattern='^add_holiday$')],
    states={
        GET_HOLIDAY_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_holiday_date)],
        GET_HOLIDAY_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_holiday_title)],
    },
    fallbacks=[MessageHandler(filters.Regex('^لغو$'), cancel_time_settings)],
)
