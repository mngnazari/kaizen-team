# database/__init__.py

"""
ماژول Database - مدیریت دیتابیس و Models
"""

from .connection import create_connection

__all__ = ['create_connection']