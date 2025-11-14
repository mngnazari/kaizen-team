# handlers/admin/manage/__init__.py

"""
Task Management Handlers - مدیریت کارها
"""

from .manage_menu_handler import show_manage_tasks_menu
from .manage_by_employee_handler import (
    manage_by_employee,
    show_employee_tasks_by_category,
    show_tasks_by_employee_category
)
from .manage_by_category_handler import (
    manage_by_category,
    show_category_tasks
)
from .manage_by_status_handler import (
    manage_by_status,
    show_tasks_by_status
)
from .manage_task_detail_handler import (
    view_task_details_admin,
    assign_task_to_employee,
    confirm_assign_task,
    change_task_status
)

__all__ = [
    'show_manage_tasks_menu',
    'manage_by_employee',
    'show_employee_tasks_by_category',
    'show_tasks_by_employee_category',
    'manage_by_category',
    'show_category_tasks',
    'manage_by_status',
    'show_tasks_by_status',
    'view_task_details_admin',
    'assign_task_to_employee',
    'confirm_assign_task',
    'change_task_status',
]