# utils/formatters.py

"""
توابع فرمت‌بندی و نمایش
"""


def format_time(minutes: int) -> str:
    """
    تبدیل دقیقه به فرمت ساعت:دقیقه

    Args:
        minutes: تعداد دقایق

    Returns:
        str: فرمت شده (مثلاً "2س 30د" یا "45د")
    """
    if minutes < 60:
        return f"{minutes}د"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}س {mins}د" if mins > 0 else f"{hours}س"


def format_time_as_hours(minutes: int) -> str:
    """
    تبدیل دقیقه به فرمت ساعت اعشاری

    Args:
        minutes: تعداد دقایق

    Returns:
        str: فرمت شده (مثلاً "1.5 ساعت" یا "2 ساعت")
    """
    if minutes == 0:
        return "0 ساعت"

    hours = minutes / 60

    # اگر عدد صحیح است
    if hours == int(hours):
        return f"{int(hours)} ساعت"
    else:
        return f"{hours:.1f} ساعت"


def format_task_status(status: str) -> str:
    """
    فرمت کردن وضعیت کار برای نمایش
    
    Args:
        status: وضعیت کار
        
    Returns:
        str: وضعیت با emoji
    """
    status_map = {
        'pending': '⏳ در انتظار',
        'in_progress': '🔄 در حال انجام',
        'completed': '✅ تکمیل شده',
        'on_hold': '⏸ متوقف شده',
        'archived': '🗄 آرشیو شده'
    }
    return status_map.get(status, 'نامشخص')


def format_user_role(role: str, is_employee: int = 0) -> str:
    """
    فرمت کردن نقش کاربر
    
    Args:
        role: نقش کاربر
        is_employee: آیا کارمند است
        
    Returns:
        str: نقش با emoji
    """
    if role == 'admin':
        return '👨‍💼 مدیر'
    elif role == 'employee' and is_employee == 1:
        return '👷 کارمند'
    elif role == 'pending':
        return '⏳ در انتظار تأیید'
    else:
        return 'نامشخص'


def format_file_type(file_type: str) -> str:
    """
    فرمت کردن نوع فایل با emoji
    
    Args:
        file_type: نوع فایل
        
    Returns:
        str: نوع فایل با emoji
    """
    file_type_map = {
        'photo': '🖼 تصویر',
        'video': '🎥 ویدیو',
        'voice': '🎤 صدا',
        'document': '📄 فایل'
    }
    return file_type_map.get(file_type, '📎 فایل')


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    کوتاه کردن متن طولانی
    
    Args:
        text: متن اصلی
        max_length: حداکثر طول
        
    Returns:
        str: متن کوتاه شده
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."


def format_date_persian(date_str: str) -> str:
    """
    فرمت کردن تاریخ به صورت خوانا
    
    Args:
        date_str: تاریخ به فرمت "%Y-%m-%d %H:%M:%S"
        
    Returns:
        str: تاریخ فرمت شده
    """
    if not date_str:
        return "ندارد"
    
    try:
        # در آینده می‌توان تبدیل به تاریخ شمسی اضافه کرد
        return date_str.split('.')[0]  # حذف microseconds
    except:
        return date_str


def format_score(score: int) -> str:
    """
    فرمت کردن امتیاز
    
    Args:
        score: امتیاز (1-10)
        
    Returns:
        str: امتیاز با ستاره
    """
    if not score:
        return "⭐ ثبت نشده"
    
    # تبدیل امتیاز به ستاره
    stars = "⭐" * (score // 2)  # تقسیم بر 2 برای نمایش بهتر
    return f"{stars} {score}/10"
