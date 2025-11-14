# handlers/admin/manage/manage_by_employee_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database.models.user import UserModel
from services.user_service import UserService
from services.task_service import TaskService


async def manage_by_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست کارمندان با آمار کارها"""
    query = update.callback_query
    await query.answer()

    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text(
            "❌ هیچ کارمندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_tasks")
            ]])
        )
        return

    keyboard = []

    # دکمه کارهای تخصیص داده نشده
    unassigned_count = TaskService.count_unassigned_tasks()
    keyboard.append([InlineKeyboardButton(
        f"📋 تخصیص داده نشده ({unassigned_count})",
        callback_data="unassigned_tasks"
    )])

    for employee in employees:
        emp_id = employee.get('id')
        name = employee.get('name')

        # دریافت آمار از TaskService
        stats = TaskService.get_employee_task_statistics(emp_id)
        total = stats.get('total', 0)
        archived = stats.get('archived', 0)

        button_text = f"👤 {name} ({archived}/{total})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"emp_tasks_{emp_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage_tasks")])

    await query.edit_message_text(
        "👥 **مدیریت کارها بر اساس کارمند**\n\n"
        "کارمند مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_employee_tasks_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش دسته‌بندی‌های کارهای یک کارمند"""
    query = update.callback_query
    await query.answer()

    employee_id = int(query.data.split('_')[2])

    # دریافت نام کارمند
    employee = UserModel.get_by_id(employee_id)
    if not employee:
        await query.edit_message_text("❌ کارمند یافت نشد!")
        return

    employee_name = employee.get('name')

    # دریافت دسته‌بندی‌ها از TaskService
    categories = TaskService.get_employee_categories_with_stats(employee_id)

    if not categories:
        await query.edit_message_text(
            f"📝 هیچ کاری برای **{employee_name}** یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_employee")
            ]]),
            parse_mode='Markdown'
        )
        return

    keyboard = []
    for category in categories:
        cat_id = category.get('id')
        cat_name = category.get('name')
        total = category.get('total', 0)
        finished = category.get('finished', 0) or 0

        button_text = f"📂 {cat_name} ({finished}/{total})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"emp_cat_{employee_id}_{cat_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_employee")])

    await query.edit_message_text(
        f"📂 **کارهای {employee_name}**\n\n"
        f"دسته‌بندی مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_unassigned_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کارهای تخصیص داده نشده"""
    query = update.callback_query
    await query.answer()

    # دریافت کارهای تخصیص داده نشده
    tasks = TaskService.get_unassigned_tasks()

    if not tasks:
        await query.edit_message_text(
            "✅ همه کارها تخصیص داده شده‌اند!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_employee")
            ]])
        )
        return

    status_emoji = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'on_hold': '⏸',
        'archived': '🗄'
    }

    keyboard = []
    for task in tasks:
        task_id = task.get('id')
        title = task.get('title')
        status = task.get('status')
        category_name = task.get('category_name', 'بدون دسته‌بندی')
        emoji = status_emoji.get(status, '❓')

        button_text = f"{emoji} {title} ({category_name})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_task_{task_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_employee")])

    await query.edit_message_text(
        f"📋 **کارهای تخصیص داده نشده**\n\n"
        f"تعداد: {len(tasks)}\n\n"
        f"برای تخصیص، روی کار کلیک کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_tasks_by_employee_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کارهای یک کارمند در یک دسته‌بندی خاص"""
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_')
    employee_id = int(parts[2])
    category_id = int(parts[3])

    # دریافت نام کارمند
    employee = UserModel.get_by_id(employee_id)
    if not employee:
        await query.edit_message_text("❌ کارمند یافت نشد!")
        return

    employee_name = employee.get('name')

    # دریافت نام دسته‌بندی
    from database.models.category import CategoryModel
    category = CategoryModel.get_by_id(category_id)
    category_name = category.get('name') if category else 'نامشخص'

    # دریافت کارها از TaskService
    tasks = TaskService.get_tasks_by_employee_and_category(employee_id, category_id)

    if not tasks:
        await query.edit_message_text(
            f"📝 هیچ کاری یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data=f"emp_tasks_{employee_id}")
            ]])
        )
        return

    status_emoji = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'on_hold': '⏸',
        'archived': '🗄'
    }

    keyboard = []
    for task in tasks:
        task_id = task.get('id')
        title = task.get('title')
        status = task.get('status')
        emoji = status_emoji.get(status, '❓')

        keyboard.append([InlineKeyboardButton(f"{emoji} {title}", callback_data=f"view_task_{task_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"emp_tasks_{employee_id}")])

    await query.edit_message_text(
        f"📋 **{employee_name} - {category_name}**\n\n"
        f"تعداد کارها: {len(tasks)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )