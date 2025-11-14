# services/review_service.py

from database.models.admin_review import AdminReviewModel
from typing import Optional, List, Dict, Any


class ReviewService:
    """سرویس مدیریت نظرات ادمین - Business Logic"""
    
    @staticmethod
    def add_opinion(task_id: int, admin_id: int, text_content: Optional[str] = None,
                    file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت نظر ادمین
        
        Args:
            task_id: آیدی کار
            admin_id: آیدی ادمین
            text_content: متن نظر
            file_id: آیدی فایل
            file_type: نوع فایل
            
        Returns:
            review_id یا None
        """
        return AdminReviewModel.create(task_id, admin_id, 'opinion', text_content, file_id, file_type)
    
    @staticmethod
    def add_positive_points(task_id: int, admin_id: int, text_content: Optional[str] = None,
                           file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت نقاط مثبت
        
        Args:
            task_id: آیدی کار
            admin_id: آیدی ادمین
            text_content: متن نقاط مثبت
            file_id: آیدی فایل
            file_type: نوع فایل
            
        Returns:
            review_id یا None
        """
        return AdminReviewModel.create(task_id, admin_id, 'positive', text_content, file_id, file_type)
    
    @staticmethod
    def add_negative_points(task_id: int, admin_id: int, text_content: Optional[str] = None,
                           file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت نقاط منفی
        
        Args:
            task_id: آیدی کار
            admin_id: آیدی ادمین
            text_content: متن نقاط منفی
            file_id: آیدی فایل
            file_type: نوع فایل
            
        Returns:
            review_id یا None
        """
        return AdminReviewModel.create(task_id, admin_id, 'negative', text_content, file_id, file_type)
    
    @staticmethod
    def add_suggestion(task_id: int, admin_id: int, text_content: Optional[str] = None,
                      file_id: Optional[str] = None, file_type: Optional[str] = None) -> Optional[int]:
        """
        ثبت پیشنهاد/انتقاد ادمین
        
        Args:
            task_id: آیدی کار
            admin_id: آیدی ادمین
            text_content: متن پیشنهاد
            file_id: آیدی فایل
            file_type: نوع فایل
            
        Returns:
            review_id یا None
        """
        return AdminReviewModel.create(task_id, admin_id, 'suggestion', text_content, file_id, file_type)
    
    @staticmethod
    def add_score(task_id: int, admin_id: int, admin_score: int,
                  text_content: Optional[str] = None) -> Optional[int]:
        """
        ثبت امتیاز ادمین
        
        Args:
            task_id: آیدی کار
            admin_id: آیدی ادمین
            admin_score: امتیاز (1-10)
            text_content: توضیحات اختیاری
            
        Returns:
            review_id یا None
        """
        return AdminReviewModel.create(task_id, admin_id, 'score', text_content, 
                                      admin_score=admin_score)
    
    @staticmethod
    def get_all_reviews(task_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        دریافت تمام نظرات ادمین برای یک کار
        
        Args:
            task_id: آیدی کار
            
        Returns:
            dict با کلیدهای 'opinion', 'positive', 'negative', 'suggestion', 'score'
        """
        return {
            'opinion': AdminReviewModel.get_by_task(task_id, 'opinion'),
            'positive': AdminReviewModel.get_by_task(task_id, 'positive'),
            'negative': AdminReviewModel.get_by_task(task_id, 'negative'),
            'suggestion': AdminReviewModel.get_by_task(task_id, 'suggestion'),
            'score': AdminReviewModel.get_by_task(task_id, 'score')
        }
    
    @staticmethod
    def get_opinions(task_id: int) -> List[Dict[str, Any]]:
        """دریافت نظرات ادمین"""
        return AdminReviewModel.get_by_task(task_id, 'opinion')
    
    @staticmethod
    def get_positive_points(task_id: int) -> List[Dict[str, Any]]:
        """دریافت نقاط مثبت"""
        return AdminReviewModel.get_by_task(task_id, 'positive')
    
    @staticmethod
    def get_negative_points(task_id: int) -> List[Dict[str, Any]]:
        """دریافت نقاط منفی"""
        return AdminReviewModel.get_by_task(task_id, 'negative')
    
    @staticmethod
    def get_suggestions(task_id: int) -> List[Dict[str, Any]]:
        """دریافت پیشنهادات ادمین"""
        return AdminReviewModel.get_by_task(task_id, 'suggestion')
    
    @staticmethod
    def get_scores(task_id: int) -> List[Dict[str, Any]]:
        """دریافت امتیازات ثبت شده"""
        return AdminReviewModel.get_by_task(task_id, 'score')
    
    @staticmethod
    def get_latest_score(task_id: int) -> Optional[int]:
        """
        دریافت آخرین امتیاز ادمین
        
        Args:
            task_id: آیدی کار
            
        Returns:
            امتیاز یا None
        """
        return AdminReviewModel.get_latest_score(task_id)
    
    @staticmethod
    def format_reviews_for_display(reviews: List[Dict[str, Any]], review_type: str) -> str:
        """
        فرمت کردن نظرات برای نمایش
        
        Args:
            reviews: لیست نظرات
            review_type: نوع نظر
            
        Returns:
            str: متن فرمت شده
        """
        type_emoji = {
            'opinion': '💭',
            'positive': '✅',
            'negative': '❌',
            'suggestion': '💡',
            'score': '⭐'
        }
        
        type_title = {
            'opinion': 'نظر شما',
            'positive': 'نقاط مثبت',
            'negative': 'نقاط منفی',
            'suggestion': 'پیشنهاد/انتقاد',
            'score': 'امتیازدهی'
        }
        
        if not reviews:
            return f"{type_emoji.get(review_type, '📝')} هیچ {type_title.get(review_type, 'نظری')} ثبت نشده است."
        
        text = f"{type_emoji.get(review_type, '📝')} {type_title.get(review_type, 'نظرات')}:\n\n"
        
        for idx, review in enumerate(reviews, 1):
            text += f"#{idx} - {review.get('timestamp', 'بدون تاریخ')}\n"
            
            if review.get('text_content'):
                text += f"{review['text_content']}\n"
            
            if review.get('admin_score'):
                text += f"امتیاز: {review['admin_score']}/10\n"
            
            if review.get('file_id'):
                file_type_text = {
                    'photo': '🖼 تصویر',
                    'video': '🎥 ویدیو',
                    'voice': '🎤 صدا',
                    'document': '📄 فایل'
                }
                text += f"{file_type_text.get(review.get('file_type'), '📎 فایل')} ضمیمه شده\n"
            
            text += "\n"
        
        return text
    
    @staticmethod
    def has_any_review(task_id: int) -> bool:
        """
        بررسی اینکه آیا ادمین هیچ نظری برای کار ثبت کرده یا نه
        
        Args:
            task_id: آیدی کار
            
        Returns:
            bool: آیا نظری ثبت شده؟
        """
        all_reviews = ReviewService.get_all_reviews(task_id)
        return any(len(reviews) > 0 for reviews in all_reviews.values())
    
    @staticmethod
    def get_review_summary(task_id: int) -> str:
        """
        خلاصه‌ای از نظرات ادمین
        
        Args:
            task_id: آیدی کار
            
        Returns:
            str: خلاصه نظرات
        """
        all_reviews = ReviewService.get_all_reviews(task_id)
        
        opinion_count = len(all_reviews['opinion'])
        positive_count = len(all_reviews['positive'])
        negative_count = len(all_reviews['negative'])
        suggestion_count = len(all_reviews['suggestion'])
        
        latest_score = ReviewService.get_latest_score(task_id)
        
        summary = "📊 خلاصه نظرات ادمین:\n\n"
        summary += f"💭 نظرات: {opinion_count}\n"
        summary += f"✅ نقاط مثبت: {positive_count}\n"
        summary += f"❌ نقاط منفی: {negative_count}\n"
        summary += f"💡 پیشنهادات: {suggestion_count}\n"
        
        if latest_score:
            summary += f"⭐ آخرین امتیاز: {latest_score}/10\n"
        else:
            summary += "⭐ امتیاز: ثبت نشده\n"
        
        return summary
    
    @staticmethod
    def delete_task_reviews(task_id: int) -> bool:
        """
        حذف تمام نظرات یک کار
        
        Args:
            task_id: آیدی کار
            
        Returns:
            bool: موفق بودن عملیات
        """
        return AdminReviewModel.delete_by_task(task_id)
