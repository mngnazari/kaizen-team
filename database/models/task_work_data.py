# database/models/task_work_data.py

from database.connection import create_connection
from datetime import datetime
from typing import Optional, List, Dict, Any


class TaskWorkDataModel:
    """مدل CRUD برای جدول TaskWorkData (دانش، پیشنهاد، نتایج کارمند)"""
    
    @staticmethod
    def create(task_id: int, user_id: int, data_type: str,
               text_content: Optional[str] = None, file_id: Optional[str] = None,
               file_type: Optional[str] = None) -> Optional[int]:
        """ایجاد رکورد دانش/پیشنهاد/نتایج"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO TaskWorkData 
                (task_id, user_id, data_type, text_content, file_id, file_type, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task_id, user_id, data_type, text_content, file_id, file_type, timestamp))
            
            data_id = cursor.lastrowid
            conn.commit()
            return data_id
            
        except Exception as e:
            print(f"❌ خطا در ایجاد داده کاری: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_task(task_id: int, data_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """دریافت داده‌های کاری یک task"""
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            if data_type:
                cursor.execute("""
                    SELECT * FROM TaskWorkData 
                    WHERE task_id = ? AND data_type = ?
                    ORDER BY timestamp ASC
                """, (task_id, data_type))
            else:
                cursor.execute("""
                    SELECT * FROM TaskWorkData 
                    WHERE task_id = ?
                    ORDER BY timestamp ASC
                """, (task_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت داده‌های کاری: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_task_and_user(task_id: int, user_id: int, data_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """دریافت داده‌های کاری یک کارمند در یک task"""
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            if data_type:
                cursor.execute("""
                    SELECT * FROM TaskWorkData 
                    WHERE task_id = ? AND user_id = ? AND data_type = ?
                    ORDER BY timestamp ASC
                """, (task_id, user_id, data_type))
            else:
                cursor.execute("""
                    SELECT * FROM TaskWorkData 
                    WHERE task_id = ? AND user_id = ?
                    ORDER BY timestamp ASC
                """, (task_id, user_id))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت داده‌های کاری: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def delete_by_task(task_id: int) -> bool:
        """حذف تمام داده‌های کاری یک task"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TaskWorkData WHERE task_id = ?", (task_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ خطا در حذف داده‌های کاری: {e}")
            return False
        finally:
            conn.close()
