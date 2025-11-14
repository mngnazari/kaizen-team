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
        is_employee = user.get('is_employee')  # ✅ استفاده از dictionary
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
    if user and user.get('is_employee') == 1:  # ✅ اصلاح شد
        await update.message.reply_text(
            "📋 منوی کاری شما:",
            reply_markup=get_employee_main_keyboard()
        )