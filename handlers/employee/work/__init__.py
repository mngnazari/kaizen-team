# handlers/employee/work/__init__.py

"""
Employee Work Handlers - مدیریت کارهای کارمندان
"""

from .work_panel_handler import show_task_work_panel
from .work_timer_handler import start_work_timer, end_work_timer
from .work_knowledge_handler import knowledge_conv_handler, start_knowledge_entry
from .work_suggestion_handler import suggestion_conv_handler, start_suggestion_entry
from .work_results_handler import results_conv_handler, start_results_entry
from .work_score_handler import score_conv_handler, start_self_score_entry
from .work_submit_handler import submit_task, submit_task_callback, confirm_submit_callback

__all__ = [
    'show_task_work_panel',
    'start_work_timer',
    'end_work_timer',
    'knowledge_conv_handler',
    'start_knowledge_entry',
    'suggestion_conv_handler',
    'start_suggestion_entry',
    'results_conv_handler',
    'start_results_entry',
    'score_conv_handler',
    'start_self_score_entry',
    'submit_task',
    'submit_task_callback',
    'confirm_submit_callback',
]