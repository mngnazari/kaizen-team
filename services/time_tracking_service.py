# services/time_tracking_service.py

from database.models.work_session import WorkSessionModel
from database.models.work_schedule import WorkScheduleModel
from database.models.holiday import HolidayModel
from database.models.daily_activity import DailyActivityModel
from database.models.task import TaskModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class TimeTrackingService:
    """سرویس مدیریت زمان و تایمر - Business Logic"""

    @staticmethod
    def start_work_day(user_id: int) -> tuple[bool, str]:
        """
        شروع روز کاری

        Returns:
            (success, message)
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # بررسی تعطیلی
        if HolidayModel.is_holiday(today):
            return False, "امروز تعطیل است!"

        # بررسی سشن فعال
        active_session = WorkSessionModel.get_active_session(user_id)
        if active_session:
            return False, "شما قبلاً روز کاری را شروع کرده‌اید!"

        # شروع سشن بیکاری (تا کاری را انتخاب کند)
        session_id = WorkSessionModel.start_session(
            user_id=user_id,
            session_type='daily_activity',
            activity_key='idle'
        )

        if session_id:
            return True, "روز کاری شما شروع شد. لطفاً یک کار را برای شروع انتخاب کنید."
        return False, "خطا در شروع روز کاری!"

    @staticmethod
    def end_work_day(user_id: int) -> tuple[bool, str]:
        """
        پایان روز کاری

        Returns:
            (success, message)
        """
        # پایان دادن به همه سشن‌های فعال
        success = WorkSessionModel.end_all_active_sessions(user_id)

        if success:
            today = datetime.now().strftime("%Y-%m-%d")
            summary = WorkSessionModel.get_daily_summary(user_id, today)

            message = (
                f"✅ روز کاری شما به پایان رسید.\n\n"
                f"📊 خلاصه امروز:\n"
                f"⏱ کار روی تسک‌ها: {summary.get('task_time', 0)} دقیقه\n"
                f"🍽 نهار و نماز: {summary.get('lunch_time', 0)} دقیقه\n"
                f"☕ استراحت: {summary.get('break_time', 0)} دقیقه\n"
                f"⏸ بیکاری: {summary.get('idle_time', 0)} دقیقه\n"
                f"📈 جمع کل: {summary.get('total_time', 0)} دقیقه"
            )
            return True, message

        return False, "خطا در پایان روز کاری!"

    @staticmethod
    def start_task(user_id: int, task_id: int) -> tuple[bool, str]:
        """
        شروع کار روی یک تسک

        Returns:
            (success, message)
        """
        # بررسی وجود تسک
        task = TaskModel.get_by_id(task_id)
        if not task:
            return False, "کار یافت نشد!"

        # بررسی تخصیص تسک به کاربر
        if task.get('assigned_to_id') != user_id:
            return False, "این کار به شما تخصیص داده نشده است!"

        # پایان دادن به سشن فعال قبلی
        active_session = WorkSessionModel.get_active_session(user_id)
        if active_session:
            WorkSessionModel.end_session(active_session['id'])

        # شروع سشن جدید
        session_id = WorkSessionModel.start_session(
            user_id=user_id,
            session_type='task',
            reference_id=task_id
        )

        if session_id:
            return True, f"تایمر کار '{task.get('title')}' شروع شد."
        return False, "خطا در شروع تایمر!"

    @staticmethod
    def start_daily_activity(user_id: int, activity_key: str) -> tuple[bool, str]:
        """
        شروع یک فعالیت روزانه (نهار، استراحت، بیکاری)

        Returns:
            (success, message)
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # دریافت اطلاعات فعالیت
        activity = DailyActivityModel.get_by_key(activity_key)
        if not activity:
            return False, "فعالیت یافت نشد!"

        # بررسی محدودیت روزانه
        can_use, remaining = DailyActivityModel.check_daily_limit(user_id, activity_key, today)
        if not can_use:
            return False, f"محدودیت روزانه {activity.get('display_name')} به پایان رسیده است!"

        # پایان دادن به سشن فعال قبلی
        active_session = WorkSessionModel.get_active_session(user_id)
        if active_session:
            WorkSessionModel.end_session(active_session['id'])

        # شروع سشن جدید
        session_id = WorkSessionModel.start_session(
            user_id=user_id,
            session_type='daily_activity',
            activity_key=activity_key
        )

        if session_id:
            message = f"تایمر {activity.get('display_name')} شروع شد."
            if activity.get('max_duration_minutes'):
                message += f"\n⏱ زمان باقی‌مانده امروز: {remaining} دقیقه"
            return True, message
        return False, "خطا در شروع فعالیت!"

    @staticmethod
    def get_current_status(user_id: int) -> Dict[str, Any]:
        """دریافت وضعیت فعلی کارمند"""
        active_session = WorkSessionModel.get_active_session(user_id)

        if not active_session:
            return {
                'is_working': False,
                'message': 'شما هنوز روز کاری را شروع نکرده‌اید.'
            }

        session_type = active_session.get('session_type')
        start_time = datetime.strptime(active_session.get('start_time'), "%Y-%m-%d %H:%M:%S")
        elapsed_minutes = int((datetime.now() - start_time).total_seconds() / 60)

        result = {
            'is_working': True,
            'session_id': active_session.get('id'),
            'session_type': session_type,
            'elapsed_minutes': elapsed_minutes,
            'start_time': active_session.get('start_time')
        }

        if session_type == 'task':
            task = TaskModel.get_by_id(active_session.get('reference_id'))
            if task:
                result['task_title'] = task.get('title')
                result['task_id'] = task.get('id')
                result['message'] = f"در حال کار روی: {task.get('title')}\n⏱ زمان سپری شده: {elapsed_minutes} دقیقه"
        elif session_type == 'daily_activity':
            activity = DailyActivityModel.get_by_key(active_session.get('activity_key'))
            if activity:
                result['activity_name'] = activity.get('display_name')
                result['activity_key'] = activity.get('activity_key')
                result['message'] = f"{activity.get('icon')} {activity.get('display_name')}\n⏱ زمان سپری شده: {elapsed_minutes} دقیقه"

        return result

    @staticmethod
    def get_unfinished_tasks_during_break(user_id: int) -> List[Dict[str, Any]]:
        """
        دریافت کارهای محول شده که هنوز تمام نشده‌اند
        (برای نمایش در گزارش استراحت)
        """
        from database.connection import create_connection

        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.importance, t.priority, t.status
                FROM Tasks t
                WHERE t.assigned_to_id = ?
                AND t.status IN ('pending', 'in_progress')
                ORDER BY t.importance ASC, t.priority ASC
            """, (user_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارهای تمام نشده: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_today_summary(user_id: int) -> Dict[str, Any]:
        """دریافت خلاصه فعالیت‌های امروز"""
        today = datetime.now().strftime("%Y-%m-%d")
        return WorkSessionModel.get_daily_summary(user_id, today)
