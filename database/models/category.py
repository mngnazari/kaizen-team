# database/models/category.py

from database.connection import create_connection
from typing import Optional, List, Dict, Any


class CategoryModel:
    """مدل CRUD برای جدول Categories"""
    
    @staticmethod
    def create(name: str) -> Optional[int]:
        """ایجاد دسته‌بندی جدید"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Categories (name) VALUES (?)", (name,))
            category_id = cursor.lastrowid
            conn.commit()
            return category_id
            
        except Exception as e:
            print(f"❌ خطا در ایجاد دسته‌بندی: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(category_id: int) -> Optional[Dict[str, Any]]:
        """دریافت دسته‌بندی با id"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"❌ خطا در دریافت دسته‌بندی: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_name(name: str) -> Optional[Dict[str, Any]]:
        """دریافت دسته‌بندی با نام"""
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Categories WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"❌ خطا در دریافت دسته‌بندی: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """دریافت تمام دسته‌بندی‌ها"""
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Categories ORDER BY name")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت دسته‌بندی‌ها: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update(category_id: int, name: str) -> bool:
        """به‌روزرسانی نام دسته‌بندی"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Categories SET name = ? WHERE id = ?", (name, category_id))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی دسته‌بندی: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete(category_id: int) -> bool:
        """حذف دسته‌بندی"""
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"❌ خطا در حذف دسته‌بندی: {e}")
            return False
        finally:
            conn.close()
