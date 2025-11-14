# services/task_service.py

from database.models.task import TaskModel
from database.models.category import CategoryModel
from database.connection import create_connection
from typing import Optional, List, Dict, Any


class TaskService:
    """سرویس مدیریت کارها - Business Logic"""

    @staticmethod
    def create_task(task_data: Dict[str, Any]) -> Optional[int]:
        """
        ایجاد کار جدید

        Args:
            task_data: دیکشنری حاوی اطلاعات کار

        Returns:
            task_id یا None
        """
        return TaskModel.create(**task_data)

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """
        دریافت تمام دسته‌بندی‌ها

        Returns:
            لیست دسته‌بندی‌ها
        """
        return CategoryModel.get_all()

    @staticmethod
    def get_task(task_id: int, with_details: bool = False) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کار

        Args:
            task_id: آیدی کار
            with_details: آیا اطلاعات کامل (با join) برگردانده شود؟

        Returns:
            dict اطلاعات کار یا None
        """
        if with_details:
            return TaskModel.get_with_details(task_id)
        return TaskModel.get_by_id(task_id)

    @staticmethod
    def get_employee_tasks(employee_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        دریافت کارهای یک کارمند

        Args:
            employee_id: آیدی کارمند
            status: وضعیت کارها (اختیاری)

        Returns:
            لیست کارها
        """
        return TaskModel.get_by_employee(employee_id, status)

    @staticmethod
    def get_tasks_by_status(status: str) -> List[Dict[str, Any]]:
        """
        دریافت کارها با وضعیت خاص

        Args:
            status: وضعیت ('pending', 'in_progress', 'completed', 'archived')

        Returns:
            لیست کارها
        """
        return TaskModel.get_by_status(status)

    @staticmethod
    def get_completed_submitted_tasks() -> List[Dict[str, Any]]:
        """
        دریافت کارهای تحویل شده

        Returns:
            لیست کارهای تحویل شده که هنوز finalize نشده‌اند
        """
        return TaskModel.get_completed_submitted()

    @staticmethod
    def get_archived_tasks() -> List[Dict[str, Any]]:
        """
        دریافت کارهای آرشیو شده

        Returns:
            لیست کارهای آرشیو
        """
        return TaskModel.get_archived()

    @staticmethod
    def update_task_status(task_id: int, status: str) -> bool:
        """
        به‌روزرسانی وضعیت کار

        Args:
            task_id: آیدی کار
            status: وضعیت جدید

        Returns:
            bool: موفق بودن عملیات
        """
        return TaskModel.update_status(task_id, status)

    @staticmethod
    def submit_task(task_id: int) -> bool:
        """
        تحویل کار توسط کارمند

        Args:
            task_id: آیدی کار

        Returns:
            bool: موفق بودن عملیات
        """
        return TaskModel.mark_as_submitted(task_id)

    @staticmethod
    def finalize_task(task_id: int) -> bool:
        """
        خاتمه کار توسط ادمین

        Args:
            task_id: آیدی کار

        Returns:
            bool: موفق بودن عملیات
        """
        return TaskModel.mark_as_finalized(task_id)

    @staticmethod
    def update_task(task_id: int, **kwargs) -> bool:
        """
        به‌روزرسانی فیلدهای کار

        Args:
            task_id: آیدی کار
            **kwargs: فیلدهای برای به‌روزرسانی

        Returns:
            bool: موفق بودن عملیات
        """
        return TaskModel.update(task_id, **kwargs)

    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        حذف کار

        Args:
            task_id: آیدی کار

        Returns:
            bool: موفق بودن عملیات
        """
        return TaskModel.delete(task_id)

    @staticmethod
    def assign_task_to_employee(task_id: int, employee_id: int) -> bool:
        """
        تخصیص کار به کارمند

        Args:
            task_id: آیدی کار
            employee_id: آیدی کارمند

        Returns:
            bool: موفق بودن عملیات
        """
        return TaskModel.update(task_id, assigned_to_id=employee_id)

    @staticmethod
    def format_task_profile(task: Dict[str, Any], include_employee: bool = True) -> str:
        """
        فرمت کردن شناسنامه کار

        Args:
            task: dict اطلاعات کار
            include_employee: آیا نام کارمند نمایش داده شود؟

        Returns:
            str: متن فرمت شده
        """
        text = f"📋 شناسنامه کار\n\n"
        text += f"عنوان: {task.get('title', 'ندارد')}\n"

        if include_employee and task.get('assigned_to_name'):
            text += f"کارمند: {task.get('assigned_to_name')}\n"

        if task.get('category_name'):
            text += f"دسته‌بندی: {task.get('category_name')}\n"

        if task.get('duration'):
            text += f"مدت زمان: {task.get('duration')} دقیقه\n"

        if task.get('results'):
            text += f"نتایج مورد انتظار: {task.get('results')}\n"

        if task.get('description'):
            text += f"توضیحات: {task.get('description')}\n"

        if task.get('importance'):
            text += f"اهمیت: {task.get('importance')}\n"

        if task.get('priority'):
            text += f"اولویت: {task.get('priority')}\n"

        if task.get('creation_date'):
            text += f"تاریخ ایجاد: {task.get('creation_date')}\n"

        if task.get('completion_date'):
            text += f"تاریخ تحویل: {task.get('completion_date')}\n"

        # وضعیت
        status_text = {
            'pending': '⏳ در انتظار',
            'in_progress': '🔄 در حال انجام',
            'completed': '✅ تکمیل شده',
            'on_hold': '⏸ متوقف شده',
            'archived': '🗄 آرشیو شده'
        }
        text += f"وضعیت: {status_text.get(task.get('status'), 'نامشخص')}\n"

        return text

    @staticmethod
    def format_task_list_item(task: Dict[str, Any]) -> str:
        """
        فرمت کردن یک آیتم در لیست کارها

        Args:
            task: dict اطلاعات کار

        Returns:
            str: متن فرمت شده
        """
        title = task.get('title', 'بدون عنوان')
        employee = task.get('employee_name', task.get('assigned_to_name', ''))

        if employee:
            return f"{title} ({employee})"
        return title

    @staticmethod
    @staticmethod
    @staticmethod
    @staticmethod
    def can_employee_submit(task_id: int, telegram_id: int) -> tuple[bool, str]:
        """
        بررسی اینکه آیا کارمند می‌تواند کار را تحویل دهد

        Args:
            task_id: آیدی کار
            telegram_id: تلگرام آیدی کارمند

        Returns:
            tuple: (می‌تواند تحویل دهد, پیام)
        """
        from database.models.user import UserModel
        from services.work_service import WorkService

        task = TaskModel.get_by_id(task_id)

        if not task:
            return False, "کار یافت نشد!"

        # تبدیل telegram_id به user.id
        user = UserModel.get_by_telegram_id(telegram_id)
        if not user:
            return False, "کاربر یافت نشد!"

        user_id = user.get('id')

        # دیباگ
        print(f"🔍 DEBUG: task_id={task_id}, telegram_id={telegram_id}, user_id={user_id}")

        if task.get('assigned_to_id') != user_id:
            return False, "این کار به شما تخصیص داده نشده است!"

        if task.get('status') == 'completed':
            return False, "این کار قبلاً تحویل داده شده است!"

        if task.get('status') == 'archived':
            return False, "این کار آرشیو شده است!"

        # چک کردن نتایج
        results = WorkService.get_task_results(task_id, user_id)
        print(f"🔍 DEBUG: تعداد نتایج = {len(results)}")
        print(f"🔍 DEBUG: نتایج = {results}")

        if not results or len(results) == 0:
            return False, "برای تحویل کار باید حداقل یک نتیجه ثبت کنید!"

        # چک کردن امتیاز خود
        self_score = WorkService.get_self_score(task_id, user_id)
        print(f"🔍 DEBUG: امتیاز = {self_score}")

        if not self_score:
            return False, "برای تحویل کار باید امتیاز خود را ثبت کنید!"

        return True, "امکان تحویل وجود دارد"

    @staticmethod
    def can_admin_finalize(task_id: int) -> tuple[bool, str]:
        """
        بررسی اینکه آیا ادمین می‌تواند کار را خاتمه دهد

        Args:
            task_id: آیدی کار

        Returns:
            tuple: (می‌تواند خاتمه دهد, پیام)
        """
        task = TaskModel.get_by_id(task_id)

        if not task:
            return False, "کار یافت نشد!"

        if task.get('status') != 'completed':
            return False, "فقط کارهای تکمیل شده قابل خاتمه هستند!"

        if not task.get('is_submitted'):
            return False, "کار هنوز توسط کارمند تحویل داده نشده است!"

        if task.get('is_finalized'):
            return False, "این کار قبلاً خاتمه یافته است!"

        return True, "امکان خاتمه وجود دارد"

    @staticmethod
    def get_tasks_for_admin_review() -> List[tuple]:
        """
        دریافت کارهای تحویل شده برای بررسی ادمین

        Returns:
            لیست از tuple: (task_id, title, employee_name, completion_date)
        """
        tasks = TaskModel.get_completed_submitted()

        result = []
        for task in tasks:
            result.append((
                task.get('id'),
                task.get('title'),
                task.get('employee_name', 'بدون نام'),
                task.get('completion_date', 'نامشخص')
            ))

        return result

    @staticmethod
    def get_task_review_info(task_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کار برای بررسی ادمین

        Args:
            task_id: آیدی کار

        Returns:
            dict اطلاعات کار
        """
        return TaskModel.get_with_details(task_id)

    # services/task_service.py

    # ... (کدهای قبلی)

    @staticmethod
    def get_employee_task_statistics(employee_id: int) -> Dict[str, int]:
        """
        دریافت آمار کارهای یک کارمند

        Args:
            employee_id: آیدی کارمند (user.id)

        Returns:
            dict: {'total': ..., 'pending': ..., 'in_progress': ..., 'completed': ..., 'archived': ...}
        """
        conn = create_connection()
        if not conn:
            return {}

        try:
            cursor = conn.cursor()

            # تعداد کل کارهای غیر آرشیو
            cursor.execute("""
                SELECT COUNT(*) FROM Tasks 
                WHERE assigned_to_id = ? AND status != 'archived'
            """, (employee_id,))
            total = cursor.fetchone()[0]

            # تعداد کارهای آرشیو
            cursor.execute("""
                SELECT COUNT(*) FROM Tasks 
                WHERE assigned_to_id = ? AND status = 'archived'
            """, (employee_id,))
            archived = cursor.fetchone()[0]

            # تعداد به تفکیک وضعیت
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM Tasks 
                WHERE assigned_to_id = ? 
                GROUP BY status
            """, (employee_id,))

            status_counts = {}
            for status, count in cursor.fetchall():
                status_counts[status] = count

            return {
                'total': total,
                'archived': archived,
                'pending': status_counts.get('pending', 0),
                'in_progress': status_counts.get('in_progress', 0),
                'completed': status_counts.get('completed', 0),
                'on_hold': status_counts.get('on_hold', 0)
            }

        except Exception as e:
            print(f"❌ خطا در دریافت آمار: {e}")
            return {}
        finally:
            conn.close()

    @staticmethod
    def get_employee_categories_with_stats(employee_id: int) -> List[Dict[str, Any]]:
        """
        دریافت دسته‌بندی‌های کارهای یک کارمند با آمار

        Args:
            employee_id: آیدی کارمند (user.id)

        Returns:
            لیست دسته‌بندی‌ها با آمار
        """
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, 
                       COUNT(t.id) as total,
                       SUM(CASE WHEN t.status = 'archived' THEN 1 ELSE 0 END) as finished
                FROM Categories c
                JOIN Tasks t ON t.category_id = c.id
                WHERE t.assigned_to_id = ?
                GROUP BY c.id, c.name
                ORDER BY c.name
            """, (employee_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت دسته‌بندی‌ها: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_tasks_by_employee_and_category(employee_id: int, category_id: int) -> List[Dict[str, Any]]:
        """
        دریافت کارهای یک کارمند در یک دسته‌بندی خاص

        Args:
            employee_id: آیدی کارمند (user.id)
            category_id: آیدی دسته‌بندی

        Returns:
            لیست کارها
        """
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* 
                FROM Tasks t
                WHERE t.assigned_to_id = ? AND t.category_id = ?
                ORDER BY t.creation_date DESC
            """, (employee_id, category_id))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارها: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def count_daily_completed_tasks(employee_id: int, date: str) -> int:
        """
        شمارش کارهای تحویل شده در یک روز خاص

        Args:
            employee_id: آیدی کارمند (user.id)
            date: تاریخ به فرمت "YYYY-MM-DD"

        Returns:
            تعداد کارها
        """
        conn = create_connection()
        if not conn:
            return 0

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM Tasks
                WHERE assigned_to_id = ?
                AND status = 'completed'
                AND DATE(completion_date) = ?
            """, (employee_id, date))

            return cursor.fetchone()[0]

        except Exception as e:
            print(f"❌ خطا در شمارش کارها: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_category_task_statistics(category_id: int) -> Dict[str, int]:
        """
        دریافت آمار کارهای یک دسته‌بندی

        Args:
            category_id: آیدی دسته‌بندی

        Returns:
            dict: {'total': ..., 'finished': ...}
        """
        conn = create_connection()
        if not conn:
            return {'total': 0, 'finished': 0}

        try:
            cursor = conn.cursor()

            # تعداد کل کارها
            cursor.execute("""
                SELECT COUNT(*) FROM Tasks
                WHERE category_id = ?
            """, (category_id,))
            total = cursor.fetchone()[0]

            # تعداد کارهای خاتمه یافته
            cursor.execute("""
                SELECT COUNT(*) FROM Tasks
                WHERE category_id = ? AND status = 'archived'
            """, (category_id,))
            finished = cursor.fetchone()[0]

            return {
                'total': total,
                'finished': finished
            }

        except Exception as e:
            print(f"❌ خطا در دریافت آمار دسته‌بندی: {e}")
            return {'total': 0, 'finished': 0}
        finally:
            conn.close()

    @staticmethod
    def get_tasks_count_by_status() -> Dict[str, int]:
        """
        دریافت تعداد کارها به تفکیک وضعیت

        Returns:
            dict: {'pending': ..., 'in_progress': ..., 'completed': ..., 'on_hold': ..., 'archived': ...}
        """
        conn = create_connection()
        if not conn:
            return {}

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM Tasks
                GROUP BY status
            """)

            result = {}
            for row in cursor.fetchall():
                result[row['status']] = row['count']

            return result

        except Exception as e:
            print(f"❌ خطا در دریافت آمار وضعیت‌ها: {e}")
            return {}
        finally:
            conn.close()

    @staticmethod
    def get_tasks_by_category(category_id: int) -> List[Dict[str, Any]]:
        """
        دریافت تمام کارهای یک دسته‌بندی

        Args:
            category_id: آیدی دسته‌بندی

        Returns:
            لیست کارها با اطلاعات کامل
        """
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, u.name as assigned_to_name
                FROM Tasks t
                LEFT JOIN Users u ON t.assigned_to_id = u.id
                WHERE t.category_id = ?
                ORDER BY t.creation_date DESC
            """, (category_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارهای دسته‌بندی: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def count_unassigned_tasks() -> int:
        """
        شمارش کارهای تخصیص داده نشده

        Returns:
            تعداد کارهایی که assigned_to_id آنها NULL است
        """
        conn = create_connection()
        if not conn:
            return 0

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM Tasks
                WHERE assigned_to_id IS NULL
            """)
            return cursor.fetchone()[0]

        except Exception as e:
            print(f"❌ خطا در شمارش کارهای تخصیص نیافته: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def get_unassigned_tasks() -> List[Dict[str, Any]]:
        """
        دریافت کارهای تخصیص داده نشده

        Returns:
            لیست کارهایی که assigned_to_id آنها NULL است
        """
        conn = create_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, c.name as category_name
                FROM Tasks t
                LEFT JOIN Categories c ON t.category_id = c.id
                WHERE t.assigned_to_id IS NULL
                ORDER BY t.creation_date DESC
            """)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ خطا در دریافت کارهای تخصیص نیافته: {e}")
            return []
        finally:
            conn.close()