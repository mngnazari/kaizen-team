# services/user_service.py

from database.models.user import UserModel
from typing import Optional, List, Dict, Any


class UserService:
    """سرویس مدیریت کاربران - Business Logic"""

    @staticmethod
    def register_user(telegram_id: int, first_name: str, last_name: str,
                      phone_number: Optional[str] = None) -> bool:
        """
        ثبت‌نام کاربر جدید

        Args:
            telegram_id: آیدی تلگرام
            first_name: نام
            last_name: نام خانوادگی
            phone_number: شماره تلفن

        Returns:
            bool: موفق بودن عملیات
        """
        return UserModel.create(telegram_id, first_name, last_name, phone_number)

    @staticmethod
    def get_user_info(telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کاربر

        Args:
            telegram_id: آیدی تلگرام

        Returns:
            dict با اطلاعات کاربر یا None
        """
        return UserModel.get_by_telegram_id(telegram_id)

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت کاربر با database id

        Args:
            user_id: آیدی دیتابیس

        Returns:
            dict با اطلاعات کاربر یا None
        """
        return UserModel.get_by_id(user_id)

    @staticmethod
    def get_pending_users() -> List[Dict[str, Any]]:
        """
        دریافت کاربران در انتظار تأیید

        Returns:
            لیست کاربران pending
        """
        return UserModel.get_all_pending()

    @staticmethod
    def get_all_employees() -> List[Dict[str, Any]]:
        """
        دریافت لیست کارمندان تأیید شده

        Returns:
            لیست کارمندان
        """
        return UserModel.get_all_employees()

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """
        دریافت تمام کاربران

        Returns:
            لیست تمام کاربران
        """
        return UserModel.get_all()

    @staticmethod
    def approve_employee(telegram_id: int) -> bool:
        """
        تأیید کاربر به عنوان کارمند

        Args:
            telegram_id: آیدی تلگرام

        Returns:
            bool: موفق بودن عملیات
        """
        return UserModel.approve_as_employee(telegram_id)

    @staticmethod
    def is_admin(telegram_id: int) -> bool:
        """
        بررسی ادمین بودن

        Args:
            telegram_id: آیدی تلگرام

        Returns:
            bool: ادمین است یا نه
        """
        return UserModel.is_admin(telegram_id)

    @staticmethod
    def is_employee(telegram_id: int) -> bool:
        """
        بررسی کارمند بودن

        Args:
            telegram_id: آیدی تلگرام

        Returns:
            bool: کارمند است یا نه
        """
        return UserModel.is_employee(telegram_id)

    @staticmethod
    def get_user_role(telegram_id: int) -> Optional[str]:
        """
        دریافت نقش کاربر

        Args:
            telegram_id: آیدی تلگرام

        Returns:
            'admin', 'employee', 'pending' یا None
        """
        user = UserModel.get_by_telegram_id(telegram_id)
        if user:
            return user.get('role')
        return None

    @staticmethod
    def format_user_details(user: Dict[str, Any]) -> str:
        """
        فرمت کردن اطلاعات کاربر برای نمایش

        Args:
            user: dict اطلاعات کاربر

        Returns:
            str: متن فرمت شده
        """
        role_text = {
            'admin': '👨‍💼 مدیر',
            'employee': '👷 کارمند',
            'pending': '⏳ در انتظار تأیید'
        }

        text = (
            f"👤 اطلاعات کاربر\n\n"
            f"نام: {user.get('name', 'ندارد')}\n"
            f"نقش: {role_text.get(user.get('role'), 'نامشخص')}\n"
            f"تاریخ ثبت‌نام: {user.get('registration_date', 'ندارد')}\n"
        )

        if user.get('approved_date'):
            text += f"تاریخ تأیید: {user.get('approved_date')}\n"

        if user.get('phone_number'):
            text += f"شماره تماس: {user.get('phone_number')}\n"

        return text