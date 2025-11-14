# handlers/admin/manage/manage_task_detail_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService
from services.user_service import UserService
from services.file_service import FileService


async def view_task_details_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش جزئیات کامل کار برای ادمین"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    admin_telegram_id = query.from_user.id

    # دریافت اطلاعات کامل کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # ساخت شناسنامه خلاصه
    from utils.formatters import format_task_status

    summary_text = (
        f"📋 **جزئیات کار**\n\n"
        f"**📌 عنوان:** {task.get('title')}\n"
        f"**👤 کارمند:** {task.get('assigned_to_name', 'تخصیص نیافته')}\n"
        f"**📂 دسته‌بندی:** {task.get('category_name') or 'ندارد'}\n"
        f"**⏱ مدت زمان:** {task.get('duration') or 'تعیین نشده'} دقیقه\n"
        f"**⭐ اهمیت:** {task.get('importance') or 'ندارد'}\n"
        f"**🔥 اولویت:** {task.get('priority') or 'ندارد'}\n"
        f"**📊 وضعیت:** {format_task_status(task.get('status'))}\n"
        f"**📅 تاریخ ایجاد:** {task.get('creation_date')}\n"
    )

    if task.get('completion_date'):
        summary_text += f"**✅ تاریخ تحویل:** {task.get('completion_date')}\n"

    # دکمه‌های عملیاتی
    keyboard = []

    # تغییر وضعیت
    status_buttons = []
    current_status = task.get('status')

    if current_status != 'in_progress':
        status_buttons.append(
            InlineKeyboardButton("🔄 در حال انجام", callback_data=f"status_in_progress_{task_id}")
        )
    if current_status != 'on_hold':
        status_buttons.append(
            InlineKeyboardButton("⏸ متوقف", callback_data=f"status_on_hold_{task_id}")
        )

    if status_buttons:
        keyboard.append(status_buttons)

    # تخصیص مجدد
    if task.get('assigned_to_id'):
        keyboard.append([
            InlineKeyboardButton("🔄 تخصیص مجدد", callback_data=f"reassign_task_{task_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("👤 تخصیص به کارمند", callback_data=f"assign_task_{task_id}")
        ])

    # بازگشت
    assigned_to_id = task.get('assigned_to_id')
    if assigned_to_id:
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت", callback_data=f"emp_tasks_{assigned_to_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت", callback_data="manage_tasks")
        ])

    await query.edit_message_text(
        summary_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

    # ارسال جزئیات بیشتر
    if task.get('description'):
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text=f"📝 **توضیحات:**\n{task.get('description')}",
            parse_mode='Markdown'
        )

    # ارسال فایل‌های توضیحات
    description_files = FileService.get_section_files(task_id, 'description')
    if description_files:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="📎 **فایل‌های توضیحات:**"
        )
        for file_data in description_files:
            await FileService.send_file_to_user(
                context.bot,
                admin_telegram_id,
                file_data['file_id'],
                file_data['file_type']
            )

    if task.get('results'):
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text=f"📊 **نتایج مورد انتظار:**\n{task.get('results')}",
            parse_mode='Markdown'
        )

    # ارسال فایل‌های نتایج
    results_files = FileService.get_section_files(task_id, 'results')
    if results_files:
        await context.bot.send_message(
            chat_id=admin_telegram_id,
            text="📎 **فایل‌های نتایج:**"
        )
        for file_data in results_files:
            await FileService.send_file_to_user(
                context.bot,
                admin_telegram_id,
                file_data['file_id'],
                file_data['file_type']
            )


async def assign_task_to_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارمندان برای تخصیص کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])

    # دریافت اطلاعات کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # دریافت لیست کارمندان
    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی برای تخصیص وجود ندارد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data=f"view_task_{task_id}")
            ]])
        )
        return

    keyboard = []
    for employee in employees:
        emp_id = employee.get('id')
        name = employee.get('name')

        # جلوگیری از تخصیص به کارمند فعلی
        if emp_id == task.get('assigned_to_id'):
            continue

        keyboard.append([
            InlineKeyboardButton(f"👤 {name}", callback_data=f"assign_to_{task_id}_{emp_id}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت", callback_data=f"view_task_{task_id}")
    ])

    action_text = "تخصیص مجدد" if task.get('assigned_to_id') else "تخصیص"

    await query.edit_message_text(
        f"👥 **{action_text} کار**\n\n"
        f"📋 {task.get('title')}\n\n"
        f"لطفاً کارمند مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def confirm_assign_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید و انجام تخصیص کار"""
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_')
    task_id = int(parts[2])
    employee_id = int(parts[3])

    # دریافت اطلاعات
    task = TaskService.get_task(task_id)
    employee = UserService.get_user_by_id(employee_id)

    if not task or not employee:
        await query.edit_message_text("❌ خطا در تخصیص!")
        return

    # تخصیص کار
    success = TaskService.assign_task_to_employee(task_id, employee_id)

    if success:
        await query.edit_message_text(
            f"✅ **تخصیص موفق!**\n\n"
            f"📋 {task.get('title')}\n"
            f"👤 به {employee.get('name')} تخصیص داده شد.",
            parse_mode='Markdown'
        )

        # اطلاع‌رسانی به کارمند
        try:
            employee_telegram_id = employee.get('telegram_id')
            if employee_telegram_id:
                await context.bot.send_message(
                    chat_id=employee_telegram_id,
                    text=(
                        f"📋 **کار جدیدی به شما تخصیص داده شد!**\n\n"
                        f"**عنوان:** {task.get('title')}\n\n"
                        f"برای مشاهده جزئیات، به بخش 'کارها' مراجعه کنید."
                    ),
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"❌ خطا در اطلاع‌رسانی به کارمند: {e}")

    else:
        await query.edit_message_text("❌ خطا در تخصیص کار!")


async def change_task_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغییر وضعیت کار"""
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_')
    new_status = parts[1]
    task_id = int(parts[2])

    # دریافت اطلاعات کار
    task = TaskService.get_task(task_id, with_details=True)
    if not task:
        await query.edit_message_text("❌ کار یافت نشد!")
        return

    # تغییر وضعیت
    success = TaskService.update_task_status(task_id, new_status)

    if success:
        from utils.formatters import format_task_status

        await query.answer(
            f"✅ وضعیت به '{format_task_status(new_status)}' تغییر کرد",
            show_alert=True
        )

        # بازگشت به جزئیات کار
        context.user_data['callback_query_data'] = f"view_task_{task_id}"
        await view_task_details_admin(update, context)

    else:
        await query.answer("❌ خطا در تغییر وضعیت!", show_alert=True)