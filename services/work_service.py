# services/work_service.py

from database.models.task_work_data import TaskWorkDataModel
from database.models.task_scores import TaskScoresModel
from typing import Optional, List, Dict, Any


class WorkService:
    """سرویس مدیریت کارهای ثبت شده توسط کارمندان - Business Logic"""

    @staticmethod
    def add_knowledge(task_id: int, user_id: int, text_content: Optional[str] = None,
                      file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت دانش برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند
            text_content: متن دانش
            file_id: آیدی فایل
            file_type: نوع فایل

        Returns:
            data_id یا None
        """
        return TaskWorkDataModel.create(task_id, user_id, 'knowledge', text_content, file_id, file_type)

    @staticmethod
    def add_suggestion(task_id: int, user_id: int, text_content: Optional[str] = None,
                       file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت پیشنهاد برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند
            text_content: متن پیشنهاد
            file_id: آیدی فایل
            file_type: نوع فایل

        Returns:
            data_id یا None
        """
        return TaskWorkDataModel.create(task_id, user_id, 'suggestion', text_content, file_id, file_type)

    @staticmethod
    def add_results(task_id: int, user_id: int, text_content: Optional[str] = None,
                    file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت نتایج برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند
            text_content: متن نتایج
            file_id: آیدی فایل
            file_type: نوع فایل

        Returns:
            data_id یا None
        """
        return TaskWorkDataModel.create(task_id, user_id, 'results', text_content, file_id, file_type)

    @staticmethod
    def set_self_score(task_id: int, user_id: int, score: int) -> Optional[int]:
        """
        ثبت یا به‌روزرسانی امتیاز خود کارمند

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند
            score: امتیاز (1-10)

        Returns:
            score_id یا None
        """
        return TaskScoresModel.create_or_update(task_id, user_id, score)

    @staticmethod
    def get_self_score(task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت امتیاز خود کارمند

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند

        Returns:
            dict امتیاز یا None
        """
        return TaskScoresModel.get_by_task_and_user(task_id, user_id)

    @staticmethod
    def get_task_knowledge(task_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        دریافت تمام دانش‌های ثبت شده برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند (اختیاری)

        Returns:
            لیست دانش‌ها
        """
        if user_id:
            return TaskWorkDataModel.get_by_task_and_user(task_id, user_id, 'knowledge')
        return TaskWorkDataModel.get_by_task(task_id, 'knowledge')

    @staticmethod
    def get_task_suggestions(task_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        دریافت تمام پیشنهادهای ثبت شده برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند (اختیاری)

        Returns:
            لیست پیشنهادها
        """
        if user_id:
            return TaskWorkDataModel.get_by_task_and_user(task_id, user_id, 'suggestion')
        return TaskWorkDataModel.get_by_task(task_id, 'suggestion')

    @staticmethod
    def get_task_results(task_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        دریافت تمام نتایج ثبت شده برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند (اختیاری)

        Returns:
            لیست نتایج
        """
        if user_id:
            return TaskWorkDataModel.get_by_task_and_user(task_id, user_id, 'results')
        return TaskWorkDataModel.get_by_task(task_id, 'results')

    @staticmethod
    def get_all_work_data(task_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        دریافت تمام داده‌های کاری (دانش، پیشنهاد، نتایج) برای یک کار

        Args:
            task_id: آیدی کار

        Returns:
            dict با کلیدهای 'knowledge', 'suggestion', 'results'
        """
        return {
            'knowledge': WorkService.get_task_knowledge(task_id),
            'suggestion': WorkService.get_task_suggestions(task_id),
            'results': WorkService.get_task_results(task_id)
        }

    @staticmethod
    def get_employee_work_data(task_id: int, user_id: int) -> Dict[str, Any]:
        """
        دریافت داده‌های کاری یک کارمند خاص برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند

        Returns:
            dict با کلیدهای 'knowledge', 'suggestion', 'results', 'self_score'
        """
        return {
            'knowledge': TaskWorkDataModel.get_by_task_and_user(task_id, user_id, 'knowledge'),
            'suggestion': TaskWorkDataModel.get_by_task_and_user(task_id, user_id, 'suggestion'),
            'results': TaskWorkDataModel.get_by_task_and_user(task_id, user_id, 'results'),
            'self_score': TaskScoresModel.get_by_task_and_user(task_id, user_id)
        }

    @staticmethod
    def format_work_data_for_display(work_data: List[Dict[str, Any]], data_type: str) -> str:
        """
        فرمت کردن داده‌های کاری برای نمایش

        Args:
            work_data: لیست داده‌های کاری
            data_type: نوع داده ('knowledge', 'suggestion', 'results')

        Returns:
            str: متن فرمت شده
        """
        type_emoji = {
            'knowledge': '📚',
            'suggestion': '💡',
            'results': '📊'
        }

        type_title = {
            'knowledge': 'دانش',
            'suggestion': 'پیشنهاد',
            'results': 'نتایج'
        }

        if not work_data:
            return f"{type_emoji.get(data_type, '📝')} هیچ {type_title.get(data_type, 'داده‌ای')} ثبت نشده است."

        text = f"{type_emoji.get(data_type, '📝')} {type_title.get(data_type, 'داده‌ها')} ثبت شده:\n\n"

        for idx, item in enumerate(work_data, 1):
            text += f"#{idx} - {item.get('timestamp', 'بدون تاریخ')}\n"

            if item.get('text_content'):
                text += f"{item['text_content']}\n"

            if item.get('file_id'):
                file_type_text = {
                    'photo': '🖼 تصویر',
                    'video': '🎥 ویدیو',
                    'voice': '🎤 صدا',
                    'document': '📄 فایل'
                }
                text += f"{file_type_text.get(item.get('file_type'), '📎 فایل')} ضمیمه شده\n"

            text += "\n"

        return text

    @staticmethod
    def format_self_score_for_display(score_data: Optional[Dict[str, Any]]) -> str:
        """
        فرمت کردن امتیاز خود برای نمایش

        Args:
            score_data: dict امتیاز

        Returns:
            str: متن فرمت شده
        """
        if not score_data:
            return "⭐ هیچ امتیازی ثبت نشده است."

        score = score_data.get('self_score', 0)
        timestamp = score_data.get('timestamp', 'بدون تاریخ')

        # تبدیل امتیاز به ستاره
        stars = "⭐" * (score // 2) if score > 0 else ""

        text = f"⭐ امتیاز خود:\n\n"
        text += f"امتیاز: {stars} {score}/10\n"
        text += f"تاریخ: {timestamp}\n"

        return text

    @staticmethod
    def has_any_work_data(task_id: int, user_id: int) -> bool:
        """
        بررسی اینکه آیا کارمند هیچ داده‌ای برای کار ثبت کرده یا نه

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند

        Returns:
            bool: آیا داده‌ای ثبت شده؟
        """
        data = WorkService.get_employee_work_data(task_id, user_id)

        # بررسی دانش، پیشنهاد، نتایج
        has_work = any(len(data.get(key, [])) > 0 for key in ['knowledge', 'suggestion', 'results'])

        # بررسی امتیاز
        has_score = data.get('self_score') is not None

        return has_work or has_score

    @staticmethod
    def delete_task_work_data(task_id: int) -> bool:
        """
        حذف تمام داده‌های کاری یک کار (دانش، پیشنهاد، نتایج، امتیاز)

        Args:
            task_id: آیدی کار

        Returns:
            bool: موفق بودن عملیات
        """
        # حذف داده‌های کاری
        work_deleted = TaskWorkDataModel.delete_by_task(task_id)

        # حذف امتیازها
        scores_deleted = TaskScoresModel.delete_by_task(task_id)

        return work_deleted and scores_deleted