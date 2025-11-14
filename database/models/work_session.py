# database/models/work_session.py

from database.connection import create_connection
from typing import Optional, List, Dict, Any
from datetime import datetime


class WorkSessionModel:
    """مدل CRUD برای جدول WorkSessions"""

    @staticmethod
    def start_session(user_id: int, session_type: str, reference_id: Optional[int] = None,
                     activity_key: Optional[str] = None) -> Optional[int]:
        """شروع یک سشن کاری جدید"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO WorkSessions
                (user_id, session_type, reference_id, activity_key, start_time, date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (user_id, session_type, reference_id, activity_key, time_str, date_str))

            session_id = cursor.lastrowid
            conn.commit()
            return session_id

        except Exception as e:
            print(f"❌ خطا در شروع سشن: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def end_session(session_id: int) -> bool:
        """پایان دادن به یک سشن کاری"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # دریافت زمان شروع
            cursor.execute("""
                SELECT start_time FROM WorkSessions WHERE id = ?
            """, (session_id,))
            row = cursor.fetchone()

            if not row:
                return False

            start_time = datetime.strptime(row['start_time'], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

            # به‌روزرسانی سشن
            cursor.execute("""
                UPDATE WorkSessions
                SET end_time = ?, duration_minutes = ?, is_active = 0
                WHERE id = ?
            """, (now_str, duration_minutes, session_id))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ خطا در پایان سشن: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_active_session(user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت سشن فعال کاربر"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM WorkSessions
                WHERE user_id = ? AND is_active = 1
                ORDER BY start_time DESC
                LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"❌ خطا در دریافت سشن فعال: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_sessions_by_date(user_id: int, date: str) -> List[Dict[str, Any]]:
        """دریافت تمام سشن‌های یک روز خاص"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM WorkSessions
                WHERE user_id = ? AND date = ?
                ORDER BY start_time ASC
            """, (user_id, date))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت سشن‌های روزانه: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def end_all_active_sessions(user_id: int) -> bool:
        """پایان دادن به همه سشن‌های فعال کاربر"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # دریافت همه سشن‌های فعال
            cursor.execute("""
                SELECT id, start_time FROM WorkSessions
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            active_sessions = cursor.fetchall()

            for session in active_sessions:
                session_id = session['id']
                start_time = datetime.strptime(session['start_time'], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
                duration_minutes = int((end_time - start_time).total_seconds() / 60)

                cursor.execute("""
                    UPDATE WorkSessions
                    SET end_time = ?, duration_minutes = ?, is_active = 0
                    WHERE id = ?
                """, (now_str, duration_minutes, session_id))

            conn.commit()
            return True

        except Exception as e:
            print(f"❌ خطا در پایان سشن‌های فعال: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_daily_summary(user_id: int, date: str) -> Dict[str, Any]:
        """خلاصه فعالیت‌های روزانه"""
        conn = create_connection()
        if not conn:
            return {}

        try:
            cursor = conn.cursor()

            # زمان کل کار روی تسک‌ها
            cursor.execute("""
                SELECT SUM(duration_minutes) as total_task_time
                FROM WorkSessions
                WHERE user_id = ? AND date = ? AND session_type = 'task'
            """, (user_id, date))
            task_time = cursor.fetchone()['total_task_time'] or 0

            # زمان نهار و نماز
            cursor.execute("""
                SELECT SUM(duration_minutes) as total_lunch_time
                FROM WorkSessions
                WHERE user_id = ? AND date = ? AND activity_key = 'lunch_prayer'
            """, (user_id, date))
            lunch_time = cursor.fetchone()['total_lunch_time'] or 0

            # زمان استراحت
            cursor.execute("""
                SELECT SUM(duration_minutes) as total_break_time
                FROM WorkSessions
                WHERE user_id = ? AND date = ? AND activity_key = 'break'
            """, (user_id, date))
            break_time = cursor.fetchone()['total_break_time'] or 0

            # زمان بیکاری
            cursor.execute("""
                SELECT SUM(duration_minutes) as total_idle_time
                FROM WorkSessions
                WHERE user_id = ? AND date = ? AND activity_key = 'idle'
            """, (user_id, date))
            idle_time = cursor.fetchone()['total_idle_time'] or 0

            return {
                'date': date,
                'task_time': task_time,
                'lunch_time': lunch_time,
                'break_time': break_time,
                'idle_time': idle_time,
                'total_time': task_time + lunch_time + break_time + idle_time
            }

        except Exception as e:
            print(f"❌ خطا در دریافت خلاصه روزانه: {e}")
            return {}
        finally:
            conn.close()
