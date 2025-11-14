# database/models/task_scores.py

from database.connection import create_connection
from datetime import datetime
from typing import Optional, Dict, Any


class TaskScoresModel:
    """مدل CRUD برای جدول TaskScores (امتیاز خود کارمند)"""

    @staticmethod
    def create_or_update(task_id: int, user_id: int, self_score: int) -> Optional[int]:
        """
        ایجاد یا به‌روزرسانی امتیاز خود

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند
            self_score: امتیاز (1-10)

        Returns:
            score_id یا None
        """
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # بررسی وجود امتیاز قبلی
            cursor.execute("""
                SELECT id FROM TaskScores 
                WHERE task_id = ? AND user_id = ?
            """, (task_id, user_id))

            existing = cursor.fetchone()

            if existing:
                # به‌روزرسانی امتیاز قبلی
                cursor.execute("""
                    UPDATE TaskScores 
                    SET self_score = ?, timestamp = ?
                    WHERE task_id = ? AND user_id = ?
                """, (self_score, timestamp, task_id, user_id))
                score_id = existing['id']
            else:
                # ایجاد امتیاز جدید
                cursor.execute("""
                    INSERT INTO TaskScores 
                    (task_id, user_id, self_score, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (task_id, user_id, self_score, timestamp))
                score_id = cursor.lastrowid

            conn.commit()
            return score_id

        except Exception as e:
            print(f"❌ خطا در ثبت امتیاز: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_task_and_user(task_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت امتیاز خود کارمند برای یک کار

        Args:
            task_id: آیدی کار
            user_id: آیدی کارمند

        Returns:
            dict امتیاز یا None
        """
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM TaskScores 
                WHERE task_id = ? AND user_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (task_id, user_id))

            row = cursor.fetchone()
            return dict(row) if row else None

        except Exception as e:
            print(f"❌ خطا در دریافت امتیاز: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_by_task(task_id: int) -> list:
        """
        دریافت تمام امتیازهای خود برای یک کار

        Args:
            task_id: آیدی کار

        Returns:
            لیست امتیازها
        """
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ts.*, u.name as user_name
                FROM TaskScores ts
                JOIN Users u ON ts.user_id = u.id
                WHERE ts.task_id = ?
                ORDER BY ts.timestamp DESC
            """, (task_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت امتیازها: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def delete_by_task(task_id: int) -> bool:
        """
        حذف تمام امتیازهای یک کار

        Args:
            task_id: آیدی کار

        Returns:
            bool: موفق بودن عملیات
        """
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TaskScores WHERE task_id = ?", (task_id,))
            conn.commit()
            return True

        except Exception as e:
            print(f"❌ خطا در حذف امتیازها: {e}")
            return False
        finally:
            conn.close()