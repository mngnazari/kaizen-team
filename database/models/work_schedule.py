# database/models/work_schedule.py

from database.connection import create_connection
from typing import Optional, Dict, Any


class WorkScheduleModel:
    """مدل CRUD برای جدول WorkSchedule"""

    @staticmethod
    def create(user_id: int, start_time: str = "10:00", end_time: str = "19:00") -> Optional[int]:
        """ایجاد ساعت کاری برای کارمند"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO WorkSchedule (user_id, start_time, end_time)
                VALUES (?, ?, ?)
            """, (user_id, start_time, end_time))
            schedule_id = cursor.lastrowid
            conn.commit()
            return schedule_id

        except Exception as e:
            print(f"❌ خطا در ایجاد ساعت کاری: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت ساعت کاری یک کارمند"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM WorkSchedule
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"❌ خطا در دریافت ساعت کاری: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(user_id: int, start_time: str, end_time: str) -> bool:
        """به‌روزرسانی ساعت کاری کارمند"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # غیرفعال کردن ساعت کاری قبلی
            cursor.execute("""
                UPDATE WorkSchedule
                SET is_active = 0
                WHERE user_id = ?
            """, (user_id,))

            # ایجاد ساعت کاری جدید
            cursor.execute("""
                INSERT INTO WorkSchedule (user_id, start_time, end_time)
                VALUES (?, ?, ?)
            """, (user_id, start_time, end_time))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی ساعت کاری: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_or_create_default(user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت یا ایجاد ساعت کاری پیش‌فرض"""
        schedule = WorkScheduleModel.get_by_user_id(user_id)
        if not schedule:
            schedule_id = WorkScheduleModel.create(user_id)
            if schedule_id:
                return WorkScheduleModel.get_by_user_id(user_id)
        return schedule
