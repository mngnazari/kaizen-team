# database/models/daily_activity.py

from database.connection import create_connection
from typing import Optional, List, Dict, Any


class DailyActivityModel:
    """مدل CRUD برای جدول DailyActivities"""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """دریافت تمام فعالیت‌های روزانه"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM DailyActivities
                ORDER BY id
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت فعالیت‌های روزانه: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_key(activity_key: str) -> Optional[Dict[str, Any]]:
        """دریافت فعالیت با کلید"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM DailyActivities
                WHERE activity_key = ?
            """, (activity_key,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"❌ خطا در دریافت فعالیت: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def check_daily_limit(user_id: int, activity_key: str, date: str) -> tuple[bool, int]:
        """
        بررسی محدودیت روزانه فعالیت

        Returns:
            (can_use, remaining_minutes)
        """
        conn = create_connection()
        if not conn:
            return False, 0

        try:
            cursor = conn.cursor()

            # دریافت اطلاعات فعالیت
            cursor.execute("""
                SELECT max_duration_minutes, is_fixed_duration
                FROM DailyActivities
                WHERE activity_key = ?
            """, (activity_key,))
            activity = cursor.fetchone()

            if not activity:
                return False, 0

            max_duration = activity['max_duration_minutes']
            is_fixed = activity['is_fixed_duration']

            # اگر محدودیتی ندارد
            if max_duration is None:
                return True, 999999  # بدون محدودیت

            # محاسبه مدت زمان استفاده شده در این روز
            cursor.execute("""
                SELECT SUM(duration_minutes) as used_time
                FROM WorkSessions
                WHERE user_id = ? AND activity_key = ? AND date = ?
            """, (user_id, activity_key, date))
            result = cursor.fetchone()
            used_time = result['used_time'] or 0

            remaining = max_duration - used_time

            if is_fixed:
                # برای فعالیت‌های ثابت، فقط یکبار قابل استفاده
                return used_time == 0, max_duration if used_time == 0 else 0
            else:
                # برای فعالیت‌های متغیر، تا رسیدن به حد مجاز
                return remaining > 0, remaining

        except Exception as e:
            print(f"❌ خطا در بررسی محدودیت: {e}")
            return False, 0
        finally:
            conn.close()
