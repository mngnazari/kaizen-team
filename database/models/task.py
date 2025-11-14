# database/models/task.py

from database.connection import create_connection
from datetime import datetime
from typing import Optional, List, Dict, Any


class TaskModel:
    """مدل CRUD برای جدول Tasks"""

    @staticmethod
    def create(**kwargs) -> Optional[int]:
        """
        ایجاد کار جدید

        Args:
            **kwargs: فیلدهای کار

        Returns:
            int: task_id یا None در صورت خطا
        """
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()

            # استخراج فیلدها
            title = kwargs.get('title')
            description = kwargs.get('description')
            assigned_to_id = kwargs.get('assigned_to_id')
            assigned_by_id = kwargs.get('assigned_by_id')
            duration = kwargs.get('duration')
            results = kwargs.get('results')
            importance = kwargs.get('importance')
            priority = kwargs.get('priority')
            category_id = kwargs.get('category_id')
            status = kwargs.get('status', 'pending')
            creation_date = kwargs.get('creation_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            cursor.execute("""
                INSERT INTO Tasks 
                (title, description, assigned_to_id, assigned_by_id, duration, results, 
                 importance, priority, category_id, status, creation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, assigned_to_id, assigned_by_id, duration, results,
                  importance, priority, category_id, status, creation_date))

            task_id = cursor.lastrowid
            conn.commit()

            print(f"✅ کار ایجاد شد - ID: {task_id}, تخصیص به: {assigned_to_id}")

            return task_id

        except Exception as e:
            print(f"❌ خطا در ایجاد کار: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(task_id: int) -> Optional[Dict[str, Any]]:
        """دریافت کار با id"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"❌ خطا در دریافت کار: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_with_details(task_id: int) -> Optional[Dict[str, Any]]:
        """دریافت کار با اطلاعات کامل"""
        conn = create_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, 
                       u1.name as assigned_to_name,
                       u2.name as assigned_by_name,
                       c.name as category_name
                FROM Tasks t
                LEFT JOIN Users u1 ON t.assigned_to_id = u1.id
                LEFT JOIN Users u2 ON t.assigned_by_id = u2.id
                LEFT JOIN Categories c ON t.category_id = c.id
                WHERE t.id = ?
            """, (task_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"❌ خطا در دریافت جزئیات کار: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_employee(employee_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """دریافت کارهای یک کارمند"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            if status:
                cursor.execute("""
                    SELECT t.*, c.name as category_name
                    FROM Tasks t
                    LEFT JOIN Categories c ON t.category_id = c.id
                    WHERE t.assigned_to_id = ? AND t.status = ?
                    ORDER BY t.creation_date DESC
                """, (employee_id, status))
            else:
                cursor.execute("""
                    SELECT t.*, c.name as category_name
                    FROM Tasks t
                    LEFT JOIN Categories c ON t.category_id = c.id
                    WHERE t.assigned_to_id = ?
                    ORDER BY t.creation_date DESC
                """, (employee_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارهای کارمند: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_status(status: str) -> List[Dict[str, Any]]:
        """دریافت کارها با وضعیت خاص"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, u.name as employee_name, c.name as category_name
                FROM Tasks t
                LEFT JOIN Users u ON t.assigned_to_id = u.id
                LEFT JOIN Categories c ON t.category_id = c.id
                WHERE t.status = ?
                ORDER BY t.creation_date DESC
            """, (status,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارها: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_completed_submitted() -> List[Dict[str, Any]]:
        """دریافت کارهای تحویل شده"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, u.name as employee_name
                FROM Tasks t
                LEFT JOIN Users u ON t.assigned_to_id = u.id
                WHERE t.status = 'completed' AND t.is_submitted = 1 AND t.is_finalized = 0
                ORDER BY t.completion_date DESC
            """)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارهای تحویل شده: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_archived() -> List[Dict[str, Any]]:
        """دریافت کارهای آرشیو شده"""
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, u.name as employee_name
                FROM Tasks t
                LEFT JOIN Users u ON t.assigned_to_id = u.id
                WHERE t.is_finalized = 1
                ORDER BY t.completion_date DESC
            """)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارهای آرشیو: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def update_status(task_id: int, status: str) -> bool:
        """به‌روزرسانی وضعیت کار"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Tasks SET status = ? WHERE id = ?", (status, task_id))
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی وضعیت: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def mark_as_submitted(task_id: int) -> bool:
        """علامت‌گذاری کار به عنوان تحویل شده"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            completion_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE Tasks 
                SET status = 'completed', is_submitted = 1, completion_date = ?
                WHERE id = ?
            """, (completion_date, task_id))
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"❌ خطا در تحویل کار: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def mark_as_finalized(task_id: int) -> bool:
        """علامت‌گذاری کار به عنوان خاتمه یافته"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Tasks SET is_finalized = 1 WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"❌ خطا در خاتمه کار: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update(task_id: int, **kwargs) -> bool:
        """به‌روزرسانی فیلدهای کار"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            fields = []
            values = []

            for key, value in kwargs.items():
                fields.append(f"{key} = ?")
                values.append(value)

            if not fields:
                return False

            values.append(task_id)
            query = f"UPDATE Tasks SET {', '.join(fields)} WHERE id = ?"

            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی کار: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(task_id: int) -> bool:
        """حذف کار"""
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"❌ خطا در حذف کار: {e}")
            return False
        finally:
            conn.close()