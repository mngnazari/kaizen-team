# database/models/holiday.py

from database.connection import create_connection
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


class HolidayModel:
    """مدل CRUD برای جدول Holidays"""

    @staticmethod
    def create(holiday_date: str, title: str, holiday_type: str = 'occasional') -> Optional[int]:
        """ایجاد تعطیلی جدید"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Holidays (holiday_date, title, holiday_type)
                VALUES (?, ?, ?)
            """, (holiday_date, title, holiday_type))
            holiday_id = cursor.lastrowid
            conn.commit()
            return holiday_id

        except Exception as e:
            print(f"❌ خطا در ایجاد تعطیلی: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """دریافت تمام تعطیلات"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM Holidays
                ORDER BY holiday_date DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت تعطیلات: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_occasional_holidays() -> List[Dict[str, Any]]:
        """دریافت تعطیلات مناسبتی"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM Holidays
                WHERE holiday_type = 'occasional'
                ORDER BY holiday_date DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت تعطیلات مناسبتی: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def is_holiday(date_str: str) -> bool:
        """بررسی اینکه یک تاریخ تعطیل هست یا نه"""
        conn = create_connection()
        if not conn:
            return False

        try:
            # بررسی جمعه بودن
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj.weekday() == 4:  # جمعه = 4
                return True

            # بررسی تعطیلات مناسبتی
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM Holidays
                WHERE holiday_date = ? AND holiday_type = 'occasional'
            """, (date_str,))
            count = cursor.fetchone()[0]
            return count > 0

        except Exception as e:
            print(f"❌ خطا در بررسی تعطیلی: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(holiday_id: int) -> bool:
        """حذف تعطیلی"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM Holidays
                WHERE id = ? AND holiday_type = 'occasional'
            """, (holiday_id,))
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"❌ خطا در حذف تعطیلی: {e}")
            return False
        finally:
            conn.close()
