# handlers/admin/manage/manage_by_category_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.task_service import TaskService
from database.models.category import CategoryModel


async def manage_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست دسته‌بندی‌ها با آمار کارها"""
    query = update.callback_query
    await query.answer()

    # دریافت تمام دسته‌بندی‌ها با آمار
    categories = CategoryModel.get_all()

    if not categories:
        await query.edit_message_text(
            "❌ هیچ دسته‌بندی یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_tasks")
            ]])
        )
        return

    keyboard = []

    for category in categories:
        cat_id = category.get('id')
        name = category.get('name')

        # دریافت آمار کارهای این دسته‌بندی
        stats = TaskService.get_category_task_statistics(cat_id)
        total = stats.get('total', 0)
        finished = stats.get('finished', 0)

        button_text = f"📂 {name} ({finished}/{total})"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"cat_tasks_{cat_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage_tasks")])

    await query.edit_message_text(
        "📂 **مدیریت کارها بر اساس دسته‌بندی**\n\n"
        "دسته‌بندی مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def show_category_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کارهای یک دسته‌بندی"""
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split('_')[2])

    # دریافت نام دسته‌بندی
    category = CategoryModel.get_by_id(category_id)
    if not category:
        await query.edit_message_text("❌ دسته‌بندی یافت نشد!")
        return

    category_name = category.get('name')

    # دریافت کارهای این دسته‌بندی
    tasks = TaskService.get_tasks_by_category(category_id)

    if not tasks:
        await query.edit_message_text(
            f"📝 هیچ کاری در دسته‌بندی **{category_name}** یافت نشد!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_category")
            ]]),
            parse_mode='Markdown'
        )
        return

    # نمایش کارها با گروه‌بندی بر اساس وضعیت
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
        assigned_to_name = task.get('assigned_to_name', 'تخصیص نیافته')
        emoji = status_emoji.get(status, '❓')

        button_text = f"{emoji} {title} - {assigned_to_name}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"view_task_{task_id}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت", callback_data="manage_by_category")
    ])

    await query.edit_message_text(
        f"📂 **{category_name}**\n\n"
        f"تعداد کارها: {len(tasks)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
