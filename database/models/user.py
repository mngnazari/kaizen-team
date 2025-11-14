# database/models/user.py

from database.connection import create_connection
from datetime import datetime
from typing import Optional, List, Dict, Any


class UserModel:
    """مدل CRUD برای جدول Users"""
    
    @staticmethod
    def create(telegram_id: int, first_name: str, last_name: str, 
               phone_number: Optional[str] = None) -> bool:
        """
        ایجاد کاربر جدید
        
        Args:
            telegram_id: آیدی تلگرام کاربر
            first_name: نام
            last_name: نام خانوادگی
            phone_number: شماره تلفن (اختیاری)
            
        Returns:
            bool: موفق بودن عملیات
        """
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            full_name = f"{first_name} {last_name}".strip()
            
            cursor.execute("""
                INSERT OR IGNORE INTO Users 
                (telegram_id, first_name, last_name, name, phone_number, role, registration_date) 
                VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """, (telegram_id, first_name, last_name, full_name, phone_number, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"❌ خطا در ایجاد کاربر: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت کاربر با telegram_id
        
        Args:
            telegram_id: آیدی تلگرام
            
        Returns:
            dict یا None
        """
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"❌ خطا در دریافت کاربر: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت کاربر با id
        
        Args:
            user_id: آیدی دیتابیس
            
        Returns:
            dict یا None
        """
        conn = create_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"❌ خطا در دریافت کاربر: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_pending() -> List[Dict[str, Any]]:
        """
        دریافت کاربران در انتظار تأیید
        
        Returns:
            لیست از dict ها
        """
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, telegram_id, name, registration_date, is_employee 
                FROM Users 
                WHERE role = 'pending' OR (role = 'employee' AND is_employee = 0)
                ORDER BY registration_date DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت کاربران pending: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all_employees() -> List[Dict[str, Any]]:
        """
        دریافت لیست کارمندان
        
        Returns:
            لیست از dict ها
        """
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, telegram_id, name 
                FROM Users 
                WHERE is_employee = 1 AND role = 'employee'
                ORDER BY name
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت کارمندان: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        دریافت تمام کاربران (غیر از ادمین)
        
        Returns:
            لیست از dict ها
        """
        conn = create_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, telegram_id, name, role, is_employee, registration_date 
                FROM Users 
                WHERE role != 'admin'
                ORDER BY registration_date DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"❌ خطا در دریافت کاربران: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def approve_as_employee(telegram_id: int) -> bool:
        """
        تبدیل کاربر به کارمند
        
        Args:
            telegram_id: آیدی تلگرام
            
        Returns:
            bool: موفق بودن عملیات
        """
        conn = create_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Users 
                SET role = 'employee', is_employee = 1, approved_date = ?
                WHERE telegram_id = ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), telegram_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"❌ خطا در تأیید کارمند: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def is_admin(telegram_id: int) -> bool:
        """
        بررسی ادمین بودن کاربر
        
        Args:
            telegram_id: آیدی تلگرام
            
        Returns:
            bool: ادمین است یا نه
        """
        user = UserModel.get_by_telegram_id(telegram_id)
        return user and user.get('role') == 'admin'
    
    @staticmethod
    def is_employee(telegram_id: int) -> bool:
        """
        بررسی کارمند بودن کاربر
        
        Args:
            telegram_id: آیدی تلگرام
            
        Returns:
            bool: کارمند است یا نه
        """
        user = UserModel.get_by_telegram_id(telegram_id)
        return user and user.get('role') == 'employee' and user.get('is_employee') == 1
