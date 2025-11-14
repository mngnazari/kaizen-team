# handlers/admin/define_task_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)

from services.task_service import TaskService
from services.user_service import UserService
from services.file_service import FileService
from utils.keyboards import get_back_to_menu_keyboard
from config import ADMIN_ID

# States
(TITLE, DESCRIPTION, DESCRIPTION_WAITING, RESULTS, RESULTS_WAITING,
 DURATION, IMPORTANCE, PRIORITY, CATEGORY, ASSIGN_EMPLOYEE) = range(10)


async def start_task_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند تعریف کار"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ فقط مدیر می‌تواند کار تعریف کند.")
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data['description_files'] = []
    context.user_data['results_files'] = []

    await query.edit_message_text(
        "📝 **تعریف کار جدید**\n\n"
        "لطفاً **عنوان کار** را وارد کنید:",
        parse_mode='Markdown'
    )
    return TITLE


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت عنوان کار"""
    title = update.message.text.strip()
    context.user_data['title'] = title

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_description")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await update.message.reply_text(
        f"✅ عنوان: **{title}**\n\n"
        f"📝 حالا **توضیحات کار** را وارد کنید:\n"
        f"(می‌توانید متن، عکس، ویدیو، فایل یا صدا بفرستید)\n\n"
        f"برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return DESCRIPTION


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت توضیحات (متن یا فایل)"""
    if update.message.text:
        context.user_data['description'] = update.message.text

    # دریافت فایل
    file_type = FileService.get_file_type_from_message(update.message)
    file_id = FileService.get_file_id_from_message(update.message)

    if file_type and file_id:
        context.user_data['description_files'].append({
            'file_id': file_id,
            'file_type': file_type
        })
        print(f"✅ فایل توضیحات دریافت شد: {file_type}")

    keyboard = [
        [InlineKeyboardButton("✅ بعدی", callback_data="next_to_results")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await update.message.reply_text(
        "✅ دریافت شد!\n\n"
        "می‌توانید فایل‌های بیشتری بفرستید یا دکمه **بعدی** را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return DESCRIPTION_WAITING


async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد کردن توضیحات"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_results")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await query.edit_message_text(
        "📊 حالا **نتایج مورد انتظار** از این کار را وارد کنید:\n"
        "(می‌توانید متن، عکس، ویدیو، فایل یا صدا بفرستید)\n\n"
        "برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return RESULTS


async def next_to_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتقال به بخش نتایج"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_results")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await query.edit_message_text(
        "📊 حالا **نتایج مورد انتظار** از این کار را وارد کنید:\n"
        "(می‌توانید متن، عکس، ویدیو، فایل یا صدا بفرستید)\n\n"
        "برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return RESULTS


async def get_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت نتایج (متن یا فایل)"""
    if update.message.text:
        context.user_data['results'] = update.message.text

    # دریافت فایل
    file_type = FileService.get_file_type_from_message(update.message)
    file_id = FileService.get_file_id_from_message(update.message)

    if file_type and file_id:
        context.user_data['results_files'].append({
            'file_id': file_id,
            'file_type': file_type
        })
        print(f"✅ فایل نتایج دریافت شد: {file_type}")

    keyboard = [
        [InlineKeyboardButton("✅ بعدی", callback_data="next_to_duration")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await update.message.reply_text(
        "✅ دریافت شد!\n\n"
        "می‌توانید فایل‌های بیشتری بفرستید یا دکمه **بعدی** را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return RESULTS_WAITING


async def skip_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد کردن نتایج"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_duration")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await query.edit_message_text(
        "⏱ **مدت زمان تخصیصی** برای این کار را به دقیقه وارد کنید:\n\n"
        "مثال: 120\n\n"
        "برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return DURATION


async def next_to_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتقال به بخش مدت زمان"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_duration")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await query.edit_message_text(
        "⏱ **مدت زمان تخصیصی** برای این کار را به دقیقه وارد کنید:\n\n"
        "مثال: 120\n\n"
        "برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return DURATION


async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت مدت زمان"""
    duration = update.message.text.strip()

    if not duration.isdigit():
        await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید.")
        return DURATION

    context.user_data['duration'] = int(duration)

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_importance")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await update.message.reply_text(
        f"✅ مدت زمان: {duration} دقیقه\n\n"
        f"⭐ **اهمیت کار** را وارد کنید:\n"
        f"1 = بسیار مهم\n"
        f"2 = متوسط\n"
        f"3 = کم اهمیت\n\n"
        f"برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return IMPORTANCE


async def skip_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد کردن مدت زمان"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_importance")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await query.edit_message_text(
        "⭐ **اهمیت کار** را وارد کنید:\n"
        "1 = بسیار مهم\n"
        "2 = متوسط\n"
        "3 = کم اهمیت\n\n"
        "برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return IMPORTANCE


async def get_importance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت اهمیت"""
    importance = update.message.text.strip()

    if not importance.isdigit() or not (1 <= int(importance) <= 3):
        await update.message.reply_text("❌ لطفاً عددی بین 1 تا 3 وارد کنید.")
        return IMPORTANCE

    context.user_data['importance'] = int(importance)

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_priority")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await update.message.reply_text(
        f"✅ اهمیت: {importance}\n\n"
        f"🔥 **اولویت کار** را وارد کنید:\n"
        f"1 = اولویت بالا\n"
        f"2 = اولویت متوسط\n"
        f"3 = اولویت پایین\n\n"
        f"برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return PRIORITY


async def skip_importance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد کردن اهمیت"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏭️ رد شدن", callback_data="skip_priority")],
        [InlineKeyboardButton("❌ لغو", callback_data="cancel_task")]
    ]

    await query.edit_message_text(
        "🔥 **اولویت کار** را وارد کنید:\n"
        "1 = اولویت بالا\n"
        "2 = اولویت متوسط\n"
        "3 = اولویت پایین\n\n"
        "برای رد کردن، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return PRIORITY


async def get_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت اولویت"""
    priority = update.message.text.strip()

    if not priority.isdigit() or not (1 <= int(priority) <= 3):
        await update.message.reply_text("❌ لطفاً عددی بین 1 تا 3 وارد کنید.")
        return PRIORITY

    context.user_data['priority'] = int(priority)

    categories = TaskService.get_categories()

    if not categories:
        await update.message.reply_text("❌ دسته‌بندی موجود نیست. لطفاً ابتدا دسته‌بندی ایجاد کنید.")
        return ConversationHandler.END

    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")])

    keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_task")])

    await update.message.reply_text(
        f"✅ اولویت: {priority}\n\n"
        f"📂 **دسته‌بندی کار** را انتخاب کنید (اجباری):",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CATEGORY


async def skip_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد کردن اولویت"""
    query = update.callback_query
    await query.answer()

    categories = TaskService.get_categories()

    if not categories:
        await query.edit_message_text("❌ دسته‌بندی موجود نیست.")
        return ConversationHandler.END

    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"cat_{cat['id']}")])

    keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_task")])

    await query.edit_message_text(
        "📂 **دسته‌بندی کار** را انتخاب کنید (اجباری):",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CATEGORY


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت دسته‌بندی"""
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split('_')[1])
    context.user_data['category_id'] = category_id

    employees = UserService.get_all_employees()

    if not employees:
        await query.edit_message_text("❌ هیچ کارمندی موجود نیست.")
        return ConversationHandler.END

    keyboard = []
    for emp in employees:
        keyboard.append([InlineKeyboardButton(emp['name'], callback_data=f"emp_{emp['id']}")])

    keyboard.append([InlineKeyboardButton("⏭️ رد شدن (تخصیص بعداً)", callback_data="skip_employee")])
    keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_task")])

    await query.edit_message_text(
        "👤 **کارمند** را برای انجام این کار انتخاب کنید:\n\n"
        "(می‌توانید بعداً کارمند را تخصیص دهید)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return ASSIGN_EMPLOYEE


async def skip_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد کردن تخصیص کارمند - ذخیره کار بدون کارمند"""
    query = update.callback_query
    await query.answer()

    # ایجاد کار بدون کارمند
    task_data = {
        'title': context.user_data.get('title'),
        'description': context.user_data.get('description'),
        'results': context.user_data.get('results'),
        'duration': context.user_data.get('duration'),
        'importance': context.user_data.get('importance'),
        'priority': context.user_data.get('priority'),
        'category_id': context.user_data.get('category_id'),
        'assigned_to_id': None,  # بدون کارمند
        'assigned_by_id': ADMIN_ID
    }

    task_id = TaskService.create_task(task_data)

    if task_id:
        # ✅ ذخیره فایل‌های توضیحات
        for file_data in context.user_data.get('description_files', []):
            FileService.add_section_file(
                task_id,
                'description',
                file_data['file_id'],
                file_data['file_type']
            )

        # ✅ ذخیره فایل‌های نتایج
        for file_data in context.user_data.get('results_files', []):
            FileService.add_section_file(
                task_id,
                'results',
                file_data['file_id'],
                file_data['file_type']
            )

        await query.edit_message_text(
            f"✅ **کار با موفقیت ایجاد شد!**\n\n"
            f"📋 عنوان: {task_data['title']}\n"
            f"👤 وضعیت: تخصیص داده نشده\n\n"
            f"می‌توانید بعداً از بخش 'مدیریت کارها' آن را به کارمند تخصیص دهید.",
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ خطا در ایجاد کار!",
            reply_markup=get_back_to_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


async def assign_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تخصیص کار به کارمند و ذخیره نهایی"""
    query = update.callback_query
    await query.answer()

    employee_id = int(query.data.split('_')[1])

    # ایجاد کار
    task_data = {
        'title': context.user_data.get('title'),
        'description': context.user_data.get('description'),
        'results': context.user_data.get('results'),
        'duration': context.user_data.get('duration'),
        'importance': context.user_data.get('importance'),
        'priority': context.user_data.get('priority'),
        'category_id': context.user_data.get('category_id'),
        'assigned_to_id': employee_id,
        'assigned_by_id': ADMIN_ID
    }

    task_id = TaskService.create_task(task_data)

    if task_id:
        # ✅ ذخیره فایل‌های توضیحات
        for file_data in context.user_data.get('description_files', []):
            result = FileService.add_section_file(
                task_id,
                'description',
                file_data['file_id'],
                file_data['file_type']
            )
            print(f"✅ فایل توضیحات ذخیره شد: {result}")

        # ✅ ذخیره فایل‌های نتایج
        for file_data in context.user_data.get('results_files', []):
            result = FileService.add_section_file(
                task_id,
                'results',
                file_data['file_id'],
                file_data['file_type']
            )
            print(f"✅ فایل نتایج ذخیره شد: {result}")

        await query.edit_message_text(
            f"✅ **کار با موفقیت ایجاد شد!**\n\n"
            f"📋 عنوان: {task_data['title']}\n"
            f"👤 تخصیص به: {UserService.get_user_by_id(employee_id).get('name')}",
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ خطا در ایجاد کار!",
            reply_markup=get_back_to_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو تعریف کار"""
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.edit_message_text(
        "❌ تعریف کار لغو شد.",
        reply_markup=get_back_to_menu_keyboard()
    )
    return ConversationHandler.END


task_creation_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_task_creation, pattern='^define_task$')],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        DESCRIPTION: [
            MessageHandler(filters.ALL & ~filters.COMMAND, get_description),
            CallbackQueryHandler(skip_description, pattern='^skip_description$')
        ],
        DESCRIPTION_WAITING: [
            MessageHandler(filters.ALL & ~filters.COMMAND, get_description),
            CallbackQueryHandler(next_to_results, pattern='^next_to_results$'),
            CallbackQueryHandler(cancel_task, pattern='^cancel_task$')
        ],
        RESULTS: [
            MessageHandler(filters.ALL & ~filters.COMMAND, get_results),
            CallbackQueryHandler(skip_results, pattern='^skip_results$')
        ],
        RESULTS_WAITING: [
            MessageHandler(filters.ALL & ~filters.COMMAND, get_results),
            CallbackQueryHandler(next_to_duration, pattern='^next_to_duration$'),
            CallbackQueryHandler(cancel_task, pattern='^cancel_task$')
        ],
        DURATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration),
            CallbackQueryHandler(skip_duration, pattern='^skip_duration$')
        ],
        IMPORTANCE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_importance),
            CallbackQueryHandler(skip_importance, pattern='^skip_importance$')
        ],
        PRIORITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_priority),
            CallbackQueryHandler(skip_priority, pattern='^skip_priority$')
        ],
        CATEGORY: [
            CallbackQueryHandler(get_category, pattern='^cat_')
        ],
        ASSIGN_EMPLOYEE: [
            CallbackQueryHandler(assign_employee, pattern='^emp_'),
            CallbackQueryHandler(skip_employee, pattern='^skip_employee$')
        ]
    },
    fallbacks=[
        CallbackQueryHandler(cancel_task, pattern='^cancel_task$'),
        CommandHandler('cancel', cancel_task)
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
    allow_reentry=True
)