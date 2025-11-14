# database/models/admin_review.py

from database.connection import create_connection
from datetime import datetime
from typing import Optional, List, Dict, Any


class AdminReviewModel:
    """مدل CRUD برای جدول AdminReviews"""
    
    @staticmethod
    def create(task_id: int, admin_id: int, review_type: str,
               text_content: Optional[str] = None, file_id: Optional[str] = None,
               file_type: Optional[str] = None, admin_score: Optional[int] = None) -> Optional[int]:
        """ایجاد نظر ادمین"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO AdminReviews 
                (task_id, admin_id, review_type, text_content, file_id, file_type, admin_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, admin_id, review_type, text_content, file_id, file_type, admin_score, timestamp))
            
            review_id = cursor.lastrowid
            conn.commit()
            return review_id
            
        except Exception as e:
            print(f"❌ خطا در ایجاد نظر ادمین: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_task(task_id: int, review_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """دریافت نظرات ادمین برای یک کار"""
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            if review_type:
                cursor.execute("""
                    SELECT * FROM AdminReviews 
                    WHERE task_id = ? AND review_type = ?
                    ORDER BY timestamp DESC
                """, (task_id, review_type))
            else:
                cursor.execute("""
                    SELECT * FROM AdminReviews 
                    WHERE task_id = ?
                    ORDER BY timestamp DESC
                """, (task_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت نظرات: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_latest_score(task_id: int) -> Optional[int]:
        """دریافت آخرین امتیاز ادمین"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT admin_score FROM AdminReviews 
                WHERE task_id = ? AND review_type = 'score' AND admin_score IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1
            """, (task_id,))
            
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
            
        except Exception as e:
            print(f"❌ خطا در دریافت امتیاز: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete_by_task(task_id: int) -> bool:
        """حذف تمام نظرات یک کار"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM AdminReviews WHERE task_id = ?", (task_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ خطا در حذف نظرات: {e}")
            return False
        finally:
            conn.close()
