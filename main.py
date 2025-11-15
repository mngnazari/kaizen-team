# main.py
# تست اتوماتیک دیپلوی - این کامنت برای تست پوش به ریپازیتوری اضافه شده
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
)



# ایمپورت تنظیمات
try:
    from config import BOT_TOKEN, ADMIN_ID
except ImportError:
    logging.error("خطا: فایل config.py پیدا نشد یا متغیرهای مورد نیاز در آن تعریف نشده‌اند.")
    exit()

# ایمپورت راه‌اندازی دیتابیس
from database.migrations.schema import setup_database

# ایمپورت سرویس‌ها
from services.user_service import UserService

# ایمپورت utils
from utils.constants import GET_FULL_NAME, GET_PHONE
from utils.keyboards import get_main_menu_keyboard, get_employee_main_keyboard

# تنظیمات لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ایمپورت هندلرها - دسته‌بندی ادمین
from handlers.admin.category_handler import show_categories_menu, category_conv_handler

from handlers.admin.review import (
    show_completed_tasks,
    show_task_review_panel,
    show_task_profile_for_admin,
    show_employee_outputs,
    completed_tasks_conv_handler,
    finalize_task,
    confirm_finalize_task,
    show_archived_tasks_for_admin,
    view_archived_task_for_admin,
    show_admin_review_for_archived
)

from handlers.admin.define_task_handler import task_creation_conv_handler
from handlers.admin.edit_task_handler import edit_conv_handler
from handlers.admin.user_management_handler import (
    show_user_management_menu, show_user_details, request_approval_confirmation, confirm_approval
)
from handlers.admin.menu_handler import show_main_menu
from handlers.admin.daily_report_handler import (
    show_daily_report_menu, show_employee_daily_report, show_current_tasks
)
from handlers.admin.manage import (
    show_manage_tasks_menu,
    manage_by_employee,
    show_employee_tasks_by_category,
    show_tasks_by_employee_category,
    view_task_details_admin,
    assign_task_to_employee,
    confirm_assign_task,  # ✅ اضافه شد
    change_task_status
)
# ایمپورت هندلرها - نیروها
from handlers.employee.employee_archive_handler import show_archived_tasks, view_archived_task_details
from handlers.employee.employee_task_handler import (
    list_employee_tasks, view_task_details, back_to_tasks_list, employee_conv_handler
)

# ✅ ایمپورت هندلرهای جدید work
from handlers.employee.work import (
    show_task_work_panel,
    start_work_timer,
    knowledge_conv_handler,
    suggestion_conv_handler,
    results_conv_handler,
    score_conv_handler,
    submit_task_callback,
    confirm_submit_callback
)

# ایمپورت هندلر ثبت‌نام
from handlers.registration_handler import registration_conv_handler


# --- توابع کمکی ---
def get_admin_reply_keyboard():
    """کیبورد ثابت برای ادمین - همیشه در دسترس"""
    keyboard = [
        [KeyboardButton("🏠 منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_employee_reply_keyboard():
    """کیبورد ثابت برای کارمند - همیشه در دسترس"""
    keyboard = [
        [KeyboardButton("🏠 منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- هندلر اصلی برای ادمین و کارمندان موجود ---
async def handle_start_for_existing_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر برای ادمین و کارمندان تأیید شده"""
    user_id = update.effective_user.id
    context.bot_data['admin_id'] = ADMIN_ID
    context.bot_data['bot_token'] = BOT_TOKEN

    # چک ادمین
    if user_id == ADMIN_ID:
        await update.message.reply_text(
            "👋 خوش آمدید، مدیر عزیز!",
            reply_markup=get_admin_reply_keyboard()
        )
        await update.message.reply_text(
            "📋 منوی مدیریت:",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # چک کارمند تأیید شده
    user = UserService.get_user_info(user_id)
    if user:
        is_employee = user.get('is_employee')
        role = user.get('role')
        name = user.get('name')

        if is_employee == 1 and role == 'employee':
            await update.message.reply_text(
                f"👋 سلام {name} عزیز!\n\nخوش آمدید.",
                reply_markup=get_employee_reply_keyboard()
            )
            await update.message.reply_text(
                "📋 منوی کاری شما:",
                reply_markup=get_employee_main_keyboard()
            )


async def handle_main_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر برای دکمه منوی اصلی ثابت"""
    user_id = update.effective_user.id

    # چک ادمین
    if user_id == ADMIN_ID:
        await update.message.reply_text(
            "📋 منوی مدیریت:",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # چک کارمند
    user = UserService.get_user_info(user_id)
    if user and user.get('is_employee') == 1:
        await update.message.reply_text(
            "📋 منوی کاری شما:",
            reply_markup=get_employee_main_keyboard()
        )


async def back_to_main_menu_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بازگشت به منوی اصلی نیروها"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏠 منوی اصلی:",
        reply_markup=get_employee_main_keyboard()
    )


async def back_to_main_menu_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر بازگشت به منوی اصلی ادمین"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏠 منوی اصلی:",
        reply_markup=get_main_menu_keyboard()
    )


def main() -> None:
    """تابع اصلی برای اجرای بات"""
    # 🧪 تست اتوماتیک دیپلوی گیت
    print("=" * 50)
    print("🚀 تست اتوماتیک دیپلوی - بات در حال راه‌اندازی...")
    print("=" * 50)

    # حذف دیتابیس قدیمی (اختیاری)
    db_path = "task_bot.db"
    if os.path.exists(db_path):
        # os.remove(db_path)
        print("🗑 دیتابیس قدیمی موجود است.")

    # راه‌اندازی دیتابیس جدید
    setup_database()

    application = Application.builder().token(BOT_TOKEN).build()

    # ========== ConversationHandler ها ==========
    # ابتدا ConversationHandler برای ثبت‌نام (برای کاربران جدید)
    application.add_handler(registration_conv_handler)

    # بقیه ConversationHandler ها
    application.add_handler(task_creation_conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(employee_conv_handler)
    application.add_handler(category_conv_handler)

    # ✅ ConversationHandler های جدید work
    application.add_handler(knowledge_conv_handler)
    application.add_handler(suggestion_conv_handler)
    application.add_handler(results_conv_handler)
    application.add_handler(score_conv_handler)

    application.add_handler(submit_task_callback)
    application.add_handler(confirm_submit_callback)
    application.add_handler(completed_tasks_conv_handler)

    # ========== CommandHandler ==========
    # هندلر start برای ادمین و کارمندان موجود
    application.add_handler(CommandHandler("start", handle_start_for_existing_users))

    # ========== MessageHandler برای دکمه منوی اصلی ثابت ==========
    application.add_handler(MessageHandler(filters.Regex("^🏠 منوی اصلی$"), handle_main_menu_button))

    # ========== CallbackQueryHandler ها ==========

    # --- منو و ناوبری ---
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern='^show_menu$'))
    application.add_handler(CallbackQueryHandler(back_to_main_menu_from_admin, pattern='^back_to_main_menu$'))
    application.add_handler(CallbackQueryHandler(back_to_main_menu_employee, pattern='^back_to_main_menu_employee$'))

    # --- گزارش روزانه ---
    application.add_handler(CallbackQueryHandler(show_daily_report_menu, pattern='^daily_report$'))
    application.add_handler(CallbackQueryHandler(show_employee_daily_report, pattern='^daily_report_'))
    application.add_handler(CallbackQueryHandler(show_current_tasks, pattern='^current_tasks$'))

    # --- مدیریت کارها (سیستم جدید) ---
    application.add_handler(CallbackQueryHandler(show_manage_tasks_new, pattern='^manage_tasks$'))
    application.add_handler(CallbackQueryHandler(manage_by_employee, pattern='^manage_by_employee$'))
    application.add_handler(CallbackQueryHandler(show_employee_tasks_by_category, pattern='^emp_tasks_'))
    application.add_handler(CallbackQueryHandler(show_tasks_by_employee_category, pattern='^emp_cat_'))

    # --- مدیریت کارها ---
    application.add_handler(CallbackQueryHandler(show_manage_tasks_menu, pattern='^manage_tasks$'))
    application.add_handler(CallbackQueryHandler(manage_by_employee, pattern='^manage_by_employee$'))
    application.add_handler(CallbackQueryHandler(show_employee_tasks_by_category, pattern='^emp_tasks_'))
    application.add_handler(CallbackQueryHandler(show_tasks_by_employee_category, pattern='^emp_cat_'))

    # بخش‌های در حال توسعه - حذف شد
    # application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_category$'))
    # application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_importance$'))
    # application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_priority$'))
    # application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_score$'))

    # جزئیات و تخصیص کار
    application.add_handler(CallbackQueryHandler(view_task_details_admin, pattern='^view_task_'))
    application.add_handler(CallbackQueryHandler(assign_task_to_employee, pattern='^assign_task_'))
    application.add_handler(CallbackQueryHandler(assign_task_to_employee, pattern='^reassign_task_'))
    application.add_handler(CallbackQueryHandler(confirm_assign_task, pattern='^assign_to_'))
    application.add_handler(CallbackQueryHandler(change_task_status, pattern='^status_'))

    # بخش‌های در حال توسعه
    application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_category$'))
    application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_importance$'))
    application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_priority$'))
    application.add_handler(CallbackQueryHandler(manage_placeholder, pattern='^manage_by_score$'))

    # --- مدیریت کارها (سیستم قدیم - برای سازگاری) ---
    application.add_handler(CallbackQueryHandler(list_all_tasks, pattern='^list_all_tasks$'))
    application.add_handler(CallbackQueryHandler(list_pending_tasks, pattern='^list_pending_tasks$'))
    application.add_handler(CallbackQueryHandler(list_in_progress_tasks, pattern='^list_in_progress_tasks$'))
    application.add_handler(CallbackQueryHandler(list_completed_tasks_manage, pattern='^list_completed_tasks_manage$'))

    # --- جزئیات و تخصیص کار ---
    application.add_handler(CallbackQueryHandler(view_task_details_admin, pattern='^view_task_'))
    application.add_handler(CallbackQueryHandler(assign_task_to_employee, pattern='^assign_task_'))
    application.add_handler(CallbackQueryHandler(assign_task_to_employee, pattern='^reassign_task_'))
    application.add_handler(CallbackQueryHandler(change_task_status, pattern='^status_'))

    # --- دسته‌بندی‌ها ---
    application.add_handler(CallbackQueryHandler(show_categories_menu, pattern='^categories$'))

    # --- کارهای تحویل شده و خاتمه‌یافته ---
    application.add_handler(CallbackQueryHandler(show_completed_tasks, pattern='^completed_tasks$'))
    application.add_handler(CallbackQueryHandler(show_task_review_panel, pattern='^review_task_'))
    application.add_handler(CallbackQueryHandler(show_task_profile_for_admin, pattern='^task_profile_'))
    application.add_handler(CallbackQueryHandler(show_employee_outputs, pattern='^employee_outputs_'))
    application.add_handler(CallbackQueryHandler(finalize_task, pattern='^finalize_task_'))
    application.add_handler(CallbackQueryHandler(confirm_finalize_task, pattern='^confirm_finalize_'))
    application.add_handler(CallbackQueryHandler(show_archived_tasks_for_admin, pattern='^archived_tasks$'))
    application.add_handler(CallbackQueryHandler(view_archived_task_for_admin, pattern='^view_archived_'))
    application.add_handler(CallbackQueryHandler(show_admin_review_for_archived, pattern='^admin_review_archived_'))

    # --- مدیریت کاربران ---
    application.add_handler(CallbackQueryHandler(show_user_management_menu, pattern='^user_management$'))
    application.add_handler(CallbackQueryHandler(show_user_details, pattern='^user_'))
    application.add_handler(CallbackQueryHandler(request_approval_confirmation, pattern='^approve_'))
    application.add_handler(CallbackQueryHandler(confirm_approval, pattern='^confirm_approve_'))

    # --- هندلرهای نیروها ---
    application.add_handler(CallbackQueryHandler(list_employee_tasks, pattern='^list_tasks$'))
    application.add_handler(CallbackQueryHandler(view_task_details, pattern='^details_'))
    application.add_handler(CallbackQueryHandler(back_to_tasks_list, pattern='^back_to_tasks_list$'))

    # ✅ هندلرهای کار (جدید)
    application.add_handler(CallbackQueryHandler(show_task_work_panel, pattern='^work_panel_'))
    application.add_handler(CallbackQueryHandler(start_work_timer, pattern='^start_work_'))

    application.add_handler(CallbackQueryHandler(show_archived_tasks, pattern='^archive_tasks$'))
    application.add_handler(CallbackQueryHandler(view_archived_task_details, pattern='^view_archive_'))

    # اجرای بات
    print("✅ بات با موفقیت راه‌اندازی شد!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()