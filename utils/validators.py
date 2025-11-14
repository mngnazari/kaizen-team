# utils/validators.py

"""
توابع اعتبارسنجی
"""

import re


def validate_full_name(name: str) -> tuple[bool, str]:
    """
    اعتبارسنجی نام کامل
    
    Args:
        name: نام کامل
        
    Returns:
        tuple: (معتبر است, پیام خطا)
    """
    name = name.strip()
    
    if not name:
        return False, "❌ نام نمی‌تواند خالی باشد!"
    
    if len(name.split()) < 2:
        return False, "❌ لطفاً نام و نام خانوادگی خود را وارد کنید.\n\nمثال: علی احمدی"
    
    return True, ""


def validate_phone_number(phone: str) -> tuple[bool, str]:
    """
    اعتبارسنجی شماره تلفن
    
    Args:
        phone: شماره تلفن
        
    Returns:
        tuple: (معتبر است, پیام خطا)
    """
    if not phone:
        return False, "❌ شماره تلفن الزامی است!"
    
    # حذف فاصله‌ها و کاراکترهای اضافی
    phone = phone.replace(" ", "").replace("-", "").replace("+", "")
    
    # بررسی طول (شماره‌های ایرانی معمولاً 10 یا 11 رقمی هستند)
    if len(phone) < 10:
        return False, "❌ شماره تلفن نامعتبر است!"
    
    return True, ""


def validate_score(score: str) -> tuple[bool, int, str]:
    """
    اعتبارسنجی امتیاز
    
    Args:
        score: امتیاز به صورت رشته
        
    Returns:
        tuple: (معتبر است, عدد امتیاز, پیام خطا)
    """
    try:
        score_int = int(score)
        
        if score_int < 1 or score_int > 10:
            return False, 0, "❌ امتیاز باید بین 1 تا 10 باشد!"
        
        return True, score_int, ""
    
    except ValueError:
        return False, 0, "❌ لطفاً یک عدد معتبر وارد کنید!"


def validate_duration(duration: str) -> tuple[bool, int, str]:
    """
    اعتبارسنجی مدت زمان (دقیقه)
    
    Args:
        duration: مدت زمان به صورت رشته
        
    Returns:
        tuple: (معتبر است, عدد دقیقه, پیام خطا)
    """
    try:
        duration_int = int(duration)
        
        if duration_int < 1:
            return False, 0, "❌ مدت زمان باید بیشتر از صفر باشد!"
        
        if duration_int > 10000:
            return False, 0, "❌ مدت زمان خیلی زیاد است!"
        
        return True, duration_int, ""
    
    except ValueError:
        return False, 0, "❌ لطفاً یک عدد معتبر وارد کنید!"


def validate_importance(importance: str) -> tuple[bool, int, str]:
    """
    اعتبارسنجی اهمیت
    
    Args:
        importance: اهمیت به صورت رشته
        
    Returns:
        tuple: (معتبر است, عدد اهمیت, پیام خطا)
    """
    try:
        importance_int = int(importance)
        
        if importance_int < 1 or importance_int > 10:
            return False, 0, "❌ اهمیت باید بین 1 تا 10 باشد!"
        
        return True, importance_int, ""
    
    except ValueError:
        return False, 0, "❌ لطفاً یک عدد معتبر وارد کنید!"


def validate_priority(priority: str) -> tuple[bool, int, str]:
    """
    اعتبارسنجی اولویت
    
    Args:
        priority: اولویت به صورت رشته
        
    Returns:
        tuple: (معتبر است, عدد اولویت, پیام خطا)
    """
    try:
        priority_int = int(priority)
        
        if priority_int < 1 or priority_int > 10:
            return False, 0, "❌ اولویت باید بین 1 تا 10 باشد!"
        
        return True, priority_int, ""
    
    except ValueError:
        return False, 0, "❌ لطفاً یک عدد معتبر وارد کنید!"


def validate_category_name(name: str) -> tuple[bool, str]:
    """
    اعتبارسنجی نام دسته‌بندی
    
    Args:
        name: نام دسته‌بندی
        
    Returns:
        tuple: (معتبر است, پیام خطا)
    """
    name = name.strip()
    
    if not name:
        return False, "❌ نام دسته‌بندی نمی‌تواند خالی باشد!"
    
    if len(name) < 2:
        return False, "❌ نام دسته‌بندی باید حداقل 2 کاراکتر باشد!"
    
    if len(name) > 50:
        return False, "❌ نام دسته‌بندی خیلی طولانی است! (حداکثر 50 کاراکتر)"
    
    return True, ""


def validate_text_input(text: str, min_length: int = 1, max_length: int = 5000) -> tuple[bool, str]:
    """
    اعتبارسنجی ورودی متنی عمومی
    
    Args:
        text: متن ورودی
        min_length: حداقل طول
        max_length: حداکثر طول
        
    Returns:
        tuple: (معتبر است, پیام خطا)
    """
    text = text.strip()
    
    if not text:
        return False, "❌ متن نمی‌تواند خالی باشد!"
    
    if len(text) < min_length:
        return False, f"❌ متن باید حداقل {min_length} کاراکتر باشد!"
    
    if len(text) > max_length:
        return False, f"❌ متن خیلی طولانی است! (حداکثر {max_length} کاراکتر)"
    
    return True, ""
