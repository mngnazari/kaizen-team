# database/models/task_section_file.py

from database.connection import create_connection
from typing import Optional, List, Dict, Any


class TaskSectionFileModel:
    """مدل CRUD برای جدول TaskSectionFiles (فایل‌های نتایج و توضیحات)"""
    
    @staticmethod
    def create(task_id: int, section_type: str, file_id: str, file_type: str) -> Optional[int]:
        """
        ایجاد فایل برای بخش خاص
        
        Args:
            task_id: آیدی کار
            section_type: 'results' یا 'description'
            file_id: آیدی فایل تلگرام
            file_type: نوع فایل (photo, video, document, voice)
        """
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO TaskSectionFiles (task_id, section_type, file_id, file_type)
                VALUES (?, ?, ?, ?)
            """, (task_id, section_type, file_id, file_type))
            
            file_id_db = cursor.lastrowid
            conn.commit()
            return file_id_db
            
        except Exception as e:
            print(f"❌ خطا در ایجاد فایل بخش: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_task(task_id: int, section_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """دریافت فایل‌های یک کار (یا یک بخش خاص)"""
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            if section_type:
                cursor.execute("""
                    SELECT * FROM TaskSectionFiles 
                    WHERE task_id = ? AND section_type = ?
                """, (task_id, section_type))
            else:
                cursor.execute("""
                    SELECT * FROM TaskSectionFiles WHERE task_id = ?
                """, (task_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت فایل‌های بخش: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def delete_by_task(task_id: int, section_type: Optional[str] = None) -> bool:
        """حذف فایل‌های یک کار (یا یک بخش خاص)"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            if section_type:
                cursor.execute("""
                    DELETE FROM TaskSectionFiles 
                    WHERE task_id = ? AND section_type = ?
                """, (task_id, section_type))
            else:
                cursor.execute("""
                    DELETE FROM TaskSectionFiles WHERE task_id = ?
                """, (task_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ خطا در حذف فایل‌های بخش: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(file_id: int) -> bool:
        """حذف یک فایل"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TaskSectionFiles WHERE id = ?", (file_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"❌ خطا در حذف فایل: {e}")
            return False
        finally:
            conn.close()
