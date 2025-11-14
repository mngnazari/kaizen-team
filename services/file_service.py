# services/file_service.py

from database.models.task_attachment import TaskAttachmentModel
from database.models.task_section_file import TaskSectionFileModel
from telegram import Bot
from typing import Optional, List, Dict, Any


class FileService:
    """سرویس مدیریت فایل‌ها - Business Logic"""
    
    @staticmethod
    def add_task_attachment(task_id: int, file_id: str, file_type: str) -> Optional[int]:
        """
        افزودن فایل ضمیمه به کار
        
        Args:
            task_id: آیدی کار
            file_id: آیدی فایل تلگرام
            file_type: نوع فایل
            
        Returns:
            attachment_id یا None
        """
        return TaskAttachmentModel.create(task_id, file_id, file_type)
    
    @staticmethod
    def add_section_file(task_id: int, section_type: str, file_id: str, file_type: str) -> Optional[int]:
        """
        افزودن فایل به بخش خاص (results یا description)
        
        Args:
            task_id: آیدی کار
            section_type: 'results' یا 'description'
            file_id: آیدی فایل تلگرام
            file_type: نوع فایل
            
        Returns:
            file_id یا None
        """
        return TaskSectionFileModel.create(task_id, section_type, file_id, file_type)
    
    @staticmethod
    def get_task_attachments(task_id: int) -> List[Dict[str, Any]]:
        """
        دریافت فایل‌های ضمیمه کار
        
        Args:
            task_id: آیدی کار
            
        Returns:
            لیست فایل‌ها
        """
        return TaskAttachmentModel.get_by_task(task_id)
    
    @staticmethod
    def get_section_files(task_id: int, section_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        دریافت فایل‌های بخش‌های کار
        
        Args:
            task_id: آیدی کار
            section_type: 'results' یا 'description' (اختیاری)
            
        Returns:
            لیست فایل‌ها
        """
        return TaskSectionFileModel.get_by_task(task_id, section_type)
    
    @staticmethod
    async def send_file_to_user(bot: Bot, chat_id: int, file_id: str, file_type: str, 
                                 caption: Optional[str] = None) -> bool:
        """
        ارسال فایل به کاربر
        
        Args:
            bot: نمونه Bot
            chat_id: آیدی چت
            file_id: آیدی فایل تلگرام
            file_type: نوع فایل
            caption: متن توضیحات (اختیاری)
            
        Returns:
            bool: موفق بودن ارسال
        """
        try:
            if file_type == 'photo':
                await bot.send_photo(chat_id=chat_id, photo=file_id, caption=caption)
            elif file_type == 'video':
                await bot.send_video(chat_id=chat_id, video=file_id, caption=caption)
            elif file_type == 'voice':
                await bot.send_voice(chat_id=chat_id, voice=file_id, caption=caption)
            elif file_type == 'document':
                await bot.send_document(chat_id=chat_id, document=file_id, caption=caption)
            else:
                return False
            return True
        except Exception as e:
            print(f"❌ خطا در ارسال فایل: {e}")
            return False
    
    @staticmethod
    async def send_task_files_to_user(bot: Bot, chat_id: int, task_id: int) -> bool:
        """
        ارسال تمام فایل‌های یک کار به کاربر (شامل attachments و section files)
        
        Args:
            bot: نمونه Bot
            chat_id: آیدی چت
            task_id: آیدی کار
            
        Returns:
            bool: موفق بودن ارسال
        """
        success = True
        
        # ارسال فایل‌های ضمیمه
        attachments = FileService.get_task_attachments(task_id)
        for attachment in attachments:
            result = await FileService.send_file_to_user(
                bot, chat_id, attachment['file_id'], attachment['file_type']
            )
            if not result:
                success = False
        
        return success
    
    @staticmethod
    async def send_section_files_with_labels(bot: Bot, chat_id: int, task_id: int) -> bool:
        """
        ارسال فایل‌های بخش‌ها با برچسب (نتایج / توضیحات)
        
        Args:
            bot: نمونه Bot
            chat_id: آیدی چت
            task_id: آیدی کار
            
        Returns:
            bool: موفق بودن ارسال
        """
        success = True
        
        # فایل‌های نتایج
        results_files = FileService.get_section_files(task_id, 'results')
        if results_files:
            await bot.send_message(chat_id=chat_id, text="📊 فایل‌های نتایج مورد انتظار:")
            for file_data in results_files:
                result = await FileService.send_file_to_user(
                    bot, chat_id, file_data['file_id'], file_data['file_type']
                )
                if not result:
                    success = False
        
        # فایل‌های توضیحات
        description_files = FileService.get_section_files(task_id, 'description')
        if description_files:
            await bot.send_message(chat_id=chat_id, text="📝 فایل‌های توضیحات:")
            for file_data in description_files:
                result = await FileService.send_file_to_user(
                    bot, chat_id, file_data['file_id'], file_data['file_type']
                )
                if not result:
                    success = False
        
        return success
    
    @staticmethod
    def delete_task_files(task_id: int) -> bool:
        """
        حذف تمام فایل‌های یک کار
        
        Args:
            task_id: آیدی کار
            
        Returns:
            bool: موفق بودن عملیات
        """
        success = True
        
        # حذف attachments
        if not TaskAttachmentModel.delete_by_task(task_id):
            success = False
        
        # حذف section files
        if not TaskSectionFileModel.delete_by_task(task_id):
            success = False
        
        return success
    
    @staticmethod
    def delete_section_files(task_id: int, section_type: str) -> bool:
        """
        حذف فایل‌های یک بخش خاص
        
        Args:
            task_id: آیدی کار
            section_type: 'results' یا 'description'
            
        Returns:
            bool: موفق بودن عملیات
        """
        return TaskSectionFileModel.delete_by_task(task_id, section_type)
    
    @staticmethod
    def get_file_type_from_message(message) -> Optional[str]:
        """
        تشخیص نوع فایل از پیام تلگرام
        
        Args:
            message: پیام تلگرام
            
        Returns:
            'photo', 'video', 'voice', 'document' یا None
        """
        if message.photo:
            return 'photo'
        elif message.video:
            return 'video'
        elif message.voice:
            return 'voice'
        elif message.document:
            return 'document'
        return None
    
    @staticmethod
    def get_file_id_from_message(message) -> Optional[str]:
        """
        استخراج file_id از پیام تلگرام
        
        Args:
            message: پیام تلگرام
            
        Returns:
            file_id یا None
        """
        if message.photo:
            return message.photo[-1].file_id  # بزرگترین سایز
        elif message.video:
            return message.video.file_id
        elif message.voice:
            return message.voice.file_id
        elif message.document:
            return message.document.file_id
        return None
