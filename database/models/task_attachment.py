# database/models/task_attachment.py

from database.connection import create_connection
from typing import Optional, List, Dict, Any


class TaskAttachmentModel:
    """مدل CRUD برای جدول TaskAttachments"""
    
    @staticmethod
    def create(task_id: int, file_id: str, file_type: str) -> Optional[int]:
        """ایجاد فایل ضمیمه"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO TaskAttachments (task_id, file_id, file_type)
                VALUES (?, ?, ?)
            """, (task_id, file_id, file_type))
            
            attachment_id = cursor.lastrowid
            conn.commit()
            return attachment_id
            
        except Exception as e:
            print(f"❌ خطا در ایجاد فایل ضمیمه: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_task(task_id: int) -> List[Dict[str, Any]]:
        """دریافت فایل‌های ضمیمه یک کار"""
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM TaskAttachments WHERE task_id = ?
            """, (task_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت فایل‌ها: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def delete_by_task(task_id: int) -> bool:
        """حذف تمام فایل‌های ضمیمه یک کار"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TaskAttachments WHERE task_id = ?", (task_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ خطا در حذف فایل‌ها: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(attachment_id: int) -> bool:
        """حذف یک فایل ضمیمه"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TaskAttachments WHERE id = ?", (attachment_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"❌ خطا در حذف فایل: {e}")
            return False
        finally:
            conn.close()
