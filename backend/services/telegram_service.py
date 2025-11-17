"""
Telegram service for bot integration.
Handles receiving messages, downloading files, and sending responses.
"""

import logging
import os
from typing import Dict, Any, Optional
import httpx
from telegram import Bot
from telegram.error import TelegramError

from backend.core.config import settings
from backend.utils.file_utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for Telegram bot operations."""
    
    def __init__(self):
        """Initialize Telegram service."""
        self.bot = None
        self.bot_token = None
        self._initialize_bot()
    
    def _initialize_bot(self) -> None:
        """Initialize Telegram bot."""
        try:
            if not settings.TELEGRAM_BOT_TOKEN:
                logger.warning("Telegram bot token not configured")
                return
            
            if settings.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token":
                logger.warning("Telegram bot token is set to default value")
                return
            
            self.bot_token = settings.TELEGRAM_BOT_TOKEN
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
            self.bot = None
    
    async def download_voice_file(
        self,
        file_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        Download voice file from Telegram.
        
        Args:
            file_id: Telegram file ID
            user_id: User ID
            
        Returns:
            Path to downloaded file or None
        """
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return None
        
        try:
            logger.info(f"Downloading voice file: {file_id}")
            
            # Get file info
            file = await self.bot.get_file(file_id)
            
            # Create download directory
            download_dir = os.path.join(settings.LOCAL_AUDIO_DIR, user_id)
            ensure_directory_exists(download_dir)
            
            # Generate filename
            filename = f"telegram_{file_id}.ogg"
            file_path = os.path.join(download_dir, filename)
            
            # Download file
            await file.download_to_drive(file_path)
            
            logger.info(f"Voice file downloaded: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading voice file: {e}")
            return None
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Send message to Telegram chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Parse mode (HTML, Markdown)
            
        Returns:
            True if successful
        """
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info(f"Message sent to chat {chat_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def send_processing_notification(
        self,
        chat_id: int,
        input_type: str
    ) -> bool:
        """
        Send processing notification to user.
        
        Args:
            chat_id: Telegram chat ID
            input_type: Type of input (audio/text)
            
        Returns:
            True if successful
        """
        message = "⏳ Processing your "
        message += "voice message..." if input_type == "audio" else "note..."
        return await self.send_message(chat_id, message)
    
    async def send_success_notification(
        self,
        chat_id: int,
        note_data: Dict[str, Any]
    ) -> bool:
        """
        Send success notification with note details.
        
        Args:
            chat_id: Telegram chat ID
            note_data: Note data from classification
            
        Returns:
            True if successful
        """
        title = note_data.get("title", "Untitled")
        primary_tag = note_data.get("primary_tag", "Other")
        summary = note_data.get("summary", "")
        action_items = note_data.get("actionable_items", [])
        
        message = f"✅ <b>Note Saved!</b>\n\n"
        message += f"📝 <b>{title}</b>\n"
        message += f"🏷 Category: {primary_tag}\n\n"
        
        if summary:
            message += f"📄 {summary}\n\n"
        
        if action_items:
            message += f"📌 <b>Action Items:</b>\n"
            for item in action_items[:3]:  # Limit to 3
                task = item.get("task", "")
                deadline = item.get("deadline", "")
                if task:
                    message += f"  • {task}"
                    if deadline:
                        message += f" (by {deadline})"
                    message += "\n"
        
        return await self.send_message(chat_id, message)
    
    async def send_error_notification(
        self,
        chat_id: int,
        error_message: str
    ) -> bool:
        """
        Send error notification to user.
        
        Args:
            chat_id: Telegram chat ID
            error_message: Error message
            
        Returns:
            True if successful
        """
        message = f"❌ <b>Error</b>\n\n{error_message}\n\nPlease try again."
        return await self.send_message(chat_id, message)
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """
        Get download URL for a Telegram file.
        
        Args:
            file_id: Telegram file ID
            
        Returns:
            File URL or None
        """
        if not self.bot:
            return None
        
        try:
            file = await self.bot.get_file(file_id)
            return file.file_path
        except Exception as e:
            logger.error(f"Error getting file URL: {e}")
            return None
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Set webhook URL for Telegram bot.
        
        Args:
            webhook_url: Webhook URL
            
        Returns:
            True if successful
        """
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set to: {webhook_url}")
            return True
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    async def delete_webhook(self) -> bool:
        """
        Delete webhook (useful for local development with polling).
        
        Returns:
            True if successful
        """
        if not self.bot:
            return False
        
        try:
            await self.bot.delete_webhook()
            logger.info("Webhook deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        Check if Telegram service is available.
        
        Returns:
            True if bot is initialized
        """
        return self.bot is not None
    
    def format_note_summary(self, note_data: Dict[str, Any]) -> str:
        """
        Format note data as a readable summary.
        
        Args:
            note_data: Note data dictionary
            
        Returns:
            Formatted text summary
        """
        lines = []
        
        if "title" in note_data:
            lines.append(f"📝 {note_data['title']}")
        
        if "primary_tag" in note_data:
            lines.append(f"🏷 {note_data['primary_tag']}")
        
        if "summary" in note_data:
            lines.append(f"\n{note_data['summary']}")
        
        return "\n".join(lines)


# Global instance
telegram_service = TelegramService()