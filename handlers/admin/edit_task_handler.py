# handlers/admin/edit_task_handler.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import (
    ConversationHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters, CommandHandler
)
from services.user_service import UserService
from services.task_service import TaskService
from services.file_service import FileService
from services.work_service import WorkService
from services.review_service import ReviewService
import datetime

# وضعیت‌های مکالمه
(
    EDIT_SELECT_USER, EDIT_SELECT_TASK, EDIT_GET_TITLE, EDIT_GET_DURATION, EDIT_GET_RESULTS, EDIT_GET_DESCRIPTION,
    EDIT_GET_IMPORTANCE, EDIT_GET_PRIORITY, EDIT_GET_FILES, EDIT_SELECT_ASSIGNEE, EDIT_SELECT_CATEGORY
) = range(8, 19)

# دیکشنری برای ذخیره اطلاعات موقت
tasks_being_edited = {}


def get_main_menu_keyboard():
    """کیبورد منوی اصلی کامل را برمی‌گرداند."""
    keyboard = [
        [InlineKeyboardButton("تعریف کار", callback_data="define_task")],
        [InlineKeyboardButton("ویرایش کار", callback_data="edit_task")],
        [InlineKeyboardButton("مدیریت کارها", callback_data="manage_tasks")],
        [InlineKeyboardButton("دسته‌بندی‌ها", callback_data="categories")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_task_editing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند ویرایش کار"""
    query = update.callback_query
    await query.answer()

    # دریافت لیست کاربران (نیروها)
    employees = context.bot_data['employees']
    keyboard = []

    for telegram_id, name in employees.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"edit_user_{telegram_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("کدام نیرو را برای ویرایش کار انتخاب می‌کنید؟", reply_markup=reply_markup)
    return EDIT_SELECT_USER


async def select_user_for_editing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کاربر برای ویرایش کارهایش"""
    query = update.callback_query
    await query.answer()

    user_telegram_id = int(query.data.split('_')[2])
    context.user_data['selected_user_telegram_id'] = user_telegram_id

    # دریافت کارهای این کاربر
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (user_telegram_id,))
    user_db_id = cursor.fetchone()[0]

    cursor.execute("SELECT id, title FROM Tasks WHERE assigned_to_id = ?", (user_db_id,))
    tasks = cursor.fetchall()
    conn.close()

    if not tasks:
        await query.edit_message_text("این کاربر هیچ کاری ندارد.")
        return ConversationHandler.END

    keyboard = []
    for task_id, title in tasks:
        keyboard.append([InlineKeyboardButton(title, callback_data=f"edit_task_{task_id}")])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("کدام کار را ویرایش می‌کنید؟", reply_markup=reply_markup)
    return EDIT_SELECT_TASK


async def select_task_for_editing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کار برای ویرایش"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id

    # نمایش گزینه‌های قابل ویرایش
    keyboard = [
        [InlineKeyboardButton("عنوان", callback_data=f"edit_title_{task_id}")],
        [InlineKeyboardButton("مدت زمان", callback_data=f"edit_duration_{task_id}")],
        [InlineKeyboardButton("نتایج مورد انتظار", callback_data=f"edit_results_{task_id}")],
        [InlineKeyboardButton("توضیحات", callback_data=f"edit_description_{task_id}")],
        [InlineKeyboardButton("اهمیت", callback_data=f"edit_importance_{task_id}")],
        [InlineKeyboardButton("اولویت", callback_data=f"edit_priority_{task_id}")],
        [InlineKeyboardButton("فایل‌ها", callback_data=f"edit_files_{task_id}")],
        [InlineKeyboardButton("انجام‌دهنده", callback_data=f"edit_assignee_{task_id}")],
        [InlineKeyboardButton("دسته‌بندی", callback_data=f"edit_category_{task_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("کدام قسمت را ویرایش می‌کنید؟", reply_markup=reply_markup)


# توابع ویرایش فیلدهای مختلف
async def edit_title_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش عنوان کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'title'

    await query.edit_message_text("عنوان جدید کار را وارد کنید:")
    return EDIT_GET_TITLE


async def edit_duration_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش مدت زمان کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'duration'

    await query.edit_message_text("مدت زمان جدید را به دقیقه وارد کنید:")
    return EDIT_GET_DURATION


async def edit_results_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش نتایج مورد انتظار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'results'

    await query.edit_message_text("نتایج مورد انتظار جدید را وارد کنید:")
    return EDIT_GET_RESULTS


async def edit_description_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش توضیحات"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'description'

    await query.edit_message_text("توضیحات جدید را وارد کنید:")
    return EDIT_GET_DESCRIPTION


async def edit_importance_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش اهمیت"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'importance'

    await query.edit_message_text("درجه اهمیت جدید را وارد کنید (عددی بین ۱ تا ۵):")
    return EDIT_GET_IMPORTANCE


async def edit_priority_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش اولویت"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'priority'

    await query.edit_message_text("اولویت جدید را وارد کنید (عددی بین ۱ تا ۳):")
    return EDIT_GET_PRIORITY


async def edit_files_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش فایل‌ها"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'files'
    tasks_being_edited[query.from_user.id] = {"attachments": []}

    await query.edit_message_text(
        "فایل‌های جدید را ارسال کنید. برای پایان '/end' را بفرستید:"
    )
    return EDIT_GET_FILES


async def edit_assignee_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش انجام‌دهنده"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'assignee'

    employees = context.bot_data['employees']
    keyboard = []

    for telegram_id, name in employees.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"assign_edit_{telegram_id}")])

    keyboard.append([InlineKeyboardButton("بدون تخصیص", callback_data="assign_edit_None")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("انجام‌دهنده جدید را انتخاب کنید:", reply_markup=reply_markup)
    return EDIT_SELECT_ASSIGNEE


async def edit_category_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش دسته‌بندی کار"""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.split('_')[2])
    context.user_data['edit_task_id'] = task_id
    context.user_data['edit_field'] = 'category'

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Categories ORDER BY name")
    categories = cursor.fetchall()
    conn.close()

    if not categories:
        await query.edit_message_text("هیچ دسته‌بندی تعریف نشده.")
        return ConversationHandler.END

    keyboard = []
    for cat_id, cat_name in categories:
        keyboard.append([InlineKeyboardButton(cat_name, callback_data=f"set_cat_{cat_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("دسته‌بندی جدید را انتخاب کنید:", reply_markup=reply_markup)
    return EDIT_SELECT_CATEGORY


# توابع پردازش ورودی‌ها
async def process_title_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش عنوان"""
    new_title = update.message.text
    task_id = context.user_data['edit_task_id']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET title = ? WHERE id = ?", (new_title, task_id))
    conn.commit()
    conn.close()

    await update.message.reply_text("عنوان با موفقیت به‌روزرسانی شد.")
    await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


async def process_duration_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش مدت زمان"""
    try:
        new_duration = int(update.message.text)
        if new_duration <= 0:
            raise ValueError

        task_id = context.user_data['edit_task_id']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Tasks SET duration = ? WHERE id = ?", (str(new_duration), task_id))
        conn.commit()
        conn.close()

        await update.message.reply_text("مدت زمان با موفقیت به‌روزرسانی شد.")
        await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("لطفا مدت زمان را به صورت عدد صحیح مثبت وارد کنید:")
        return EDIT_GET_DURATION


async def process_results_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش نتایج"""
    new_results = update.message.text
    task_id = context.user_data['edit_task_id']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET results = ? WHERE id = ?", (new_results, task_id))
    conn.commit()
    conn.close()

    await update.message.reply_text("نتایج مورد انتظار با موفقیت به‌روزرسانی شد.")
    await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


async def process_description_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش توضیحات"""
    new_description = update.message.text
    task_id = context.user_data['edit_task_id']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET description = ? WHERE id = ?", (new_description, task_id))
    conn.commit()
    conn.close()

    await update.message.reply_text("توضیحات با موفقیت به‌روزرسانی شد.")
    await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


async def process_importance_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش اهمیت"""
    try:
        new_importance = int(update.message.text)
        if not 1 <= new_importance <= 5:
            raise ValueError

        task_id = context.user_data['edit_task_id']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Tasks SET importance = ? WHERE id = ?", (new_importance, task_id))
        conn.commit()
        conn.close()

        await update.message.reply_text("درجه اهمیت با موفقیت به‌روزرسانی شد.")
        await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("لطفا عددی بین ۱ تا ۵ وارد کنید:")
        return EDIT_GET_IMPORTANCE


async def process_priority_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش اولویت"""
    try:
        new_priority = int(update.message.text)
        if not 1 <= new_priority <= 3:
            raise ValueError

        task_id = context.user_data['edit_task_id']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Tasks SET priority = ? WHERE id = ?", (new_priority, task_id))
        conn.commit()
        conn.close()

        await update.message.reply_text("اولویت با موفقیت به‌روزرسانی شد.")
        await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("لطفا عددی بین ۱ تا ۳ وارد کنید:")
        return EDIT_GET_PRIORITY


async def process_files_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش ویرایش فایل‌ها"""
    file_info = None

    if update.message.photo:
        file_info = (update.message.photo[-1].file_id, 'photo')
    elif update.message.video:
        file_info = (update.message.video.file_id, 'video')
    elif update.message.voice:
        file_info = (update.message.voice.file_id, 'voice')
    elif update.message.document:
        file_info = (update.message.document.file_id, 'document')

    if file_info:
        tasks_being_edited[update.effective_user.id]["attachments"].append(file_info)
        await update.message.reply_text("فایل دریافت شد. می‌توانید فایل‌های بیشتری بفرستید یا '/end' را ارسال کنید.")
    else:
        await update.message.reply_text("فقط فایل‌های تصویری، ویدیویی، صوتی و اسناد قابل دریافت هستند.")

    return EDIT_GET_FILES


async def end_files_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پایان ویرایش فایل‌ها"""
    task_id = context.user_data['edit_task_id']
    attachments = tasks_being_edited.pop(update.effective_user.id)["attachments"]

    conn = create_connection()
    cursor = conn.cursor()

    # حذف فایل‌های قدیمی
    cursor.execute("DELETE FROM TaskAttachments WHERE task_id = ?", (task_id,))

    # اضافه کردن فایل‌های جدید
    for file_id, file_type in attachments:
        cursor.execute("INSERT INTO TaskAttachments (task_id, file_id, file_type) VALUES (?, ?, ?)",
                       (task_id, file_id, file_type))

    conn.commit()
    conn.close()

    await update.message.reply_text("فایل‌ها با موفقیت به‌روزرسانی شد.")
    await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


async def save_assignee_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره ویرایش انجام‌دهنده"""
    query = update.callback_query
    await query.answer()

    assignee_telegram_id = query.data.split('_')[2]
    task_id = context.user_data['edit_task_id']

    assigned_to_db_id = None
    if assignee_telegram_id != "None":
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (int(assignee_telegram_id),))
        assigned_to_db_id = cursor.fetchone()[0]
        conn.close()

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET assigned_to_id = ? WHERE id = ?", (assigned_to_db_id, task_id))
    conn.commit()
    conn.close()

    await query.edit_message_text("انجام‌دهنده با موفقیت به‌روزرسانی شد.")
    await context.bot.send_message(chat_id=query.from_user.id, text="منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


async def save_category_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره ویرایش دسته‌بندی"""
    query = update.callback_query
    await query.answer()

    category_id = int(query.data.split('_')[2])
    task_id = context.user_data['edit_task_id']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tasks SET category_id = ? WHERE id = ?", (category_id, task_id))
    conn.commit()
    conn.close()

    await query.edit_message_text("دسته‌بندی با موفقیت به‌روزرسانی شد.")
    await context.bot.send_message(chat_id=query.from_user.id, text="منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


async def cancel_edit_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ویرایش کار"""
    user_id = update.effective_user.id
    tasks_being_edited.pop(user_id, None)

    await update.message.reply_text("ویرایش کار لغو شد.")
    await update.message.reply_text("منوی اصلی:", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END


# ConversationHandler اصلی
edit_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_task_editing, pattern='^edit_task$')],
    states={
        EDIT_SELECT_USER: [
            CallbackQueryHandler(select_user_for_editing, pattern='^edit_user_'),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_SELECT_TASK: [
            CallbackQueryHandler(select_task_for_editing, pattern='^edit_task_'),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_title_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_DURATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_duration_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_RESULTS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_results_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_description_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_IMPORTANCE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_importance_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_PRIORITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_priority_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_GET_FILES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND | filters.ATTACHMENT, process_files_edit),
            CommandHandler("end", end_files_edit),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_SELECT_ASSIGNEE: [
            CallbackQueryHandler(save_assignee_edit, pattern='^assign_edit_'),
            CommandHandler("cancel", cancel_edit_task)
        ],
        EDIT_SELECT_CATEGORY: [
            CallbackQueryHandler(save_category_edit, pattern='^set_cat_'),
            CommandHandler("cancel", cancel_edit_task)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(edit_title_field, pattern='^edit_title_'),
        CallbackQueryHandler(edit_duration_field, pattern='^edit_duration_'),
        CallbackQueryHandler(edit_results_field, pattern='^edit_results_'),
        CallbackQueryHandler(edit_description_field, pattern='^edit_description_'),
        CallbackQueryHandler(edit_importance_field, pattern='^edit_importance_'),
        CallbackQueryHandler(edit_priority_field, pattern='^edit_priority_'),
        CallbackQueryHandler(edit_files_field, pattern='^edit_files_'),
        CallbackQueryHandler(edit_assignee_field, pattern='^edit_assignee_'),
        CallbackQueryHandler(edit_category_field, pattern='^edit_category_'),
        CommandHandler("cancel", cancel_edit_task)
    ],
    per_message=False
)