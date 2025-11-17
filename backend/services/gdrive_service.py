"""
Google Drive service for exporting and syncing notes.
Handles OAuth authentication and file operations.
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload
from googleapiclient.errors import HttpError

from backend.core.config import settings
from backend.utils.google_api_utils import (
    get_gdrive_service,
    refresh_gdrive_token,
    handle_google_api_error,
    log_api_usage
)

logger = logging.getLogger(__name__)


class GDriveService:
    """Service for Google Drive operations."""
    
    def __init__(self):
        """Initialize Google Drive service."""
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
    
    def create_service(self, token_data: Dict[str, Any]):
        """
        Create Google Drive service with user credentials.
        
        Args:
            token_data: OAuth token data
            
        Returns:
            Google Drive service object
        """
        try:
            credentials = Credentials.from_authorized_user_info(token_data, self.scopes)
            service = build('drive', 'v3', credentials=credentials)
            return service
        except Exception as e:
            logger.error(f"Error creating Drive service: {e}")
            raise
    
    async def export_note_as_markdown(
        self,
        note_data: Dict[str, Any],
        token_data: Dict[str, Any],
        folder_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export note as markdown file to Google Drive.
        
        Args:
            note_data: Note data dictionary
            token_data: OAuth token data
            folder_id: Google Drive folder ID (optional)
            
        Returns:
            Dictionary with file_id and file_url
        """
        try:
            logger.info(f"Exporting note to Google Drive: {note_data.get('title', 'Untitled')}")
            
            # Create Drive service
            service = self.create_service(token_data)
            
            # Generate markdown content
            markdown_content = self._generate_markdown(note_data)
            
            # Generate filename
            created_at = note_data.get('created_at', datetime.utcnow())
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            date_str = created_at.strftime('%Y-%m-%d')
            title = note_data.get('title', 'Untitled')
            # Sanitize filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{date_str}_{safe_title[:50]}.md"
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'mimeType': 'text/markdown'
            }
            
            # Add to specific folder if provided
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaInMemoryUpload(
                markdown_content.encode('utf-8'),
                mimetype='text/markdown',
                resumable=True
            )
            
            # Upload file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            file_url = file.get('webViewLink')
            
            logger.info(f"Note exported to Google Drive: {file_id}")
            log_api_usage("google_drive", "export_note", True, file_id)
            
            return {
                'file_id': file_id,
                'file_url': file_url
            }
            
        except HttpError as e:
            error_msg = handle_google_api_error(e)
            logger.error(f"Google Drive API error: {error_msg}")
            log_api_usage("google_drive", "export_note", False, error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error exporting to Google Drive: {e}")
            log_api_usage("google_drive", "export_note", False, str(e))
            raise
    
    def _generate_markdown(self, note_data: Dict[str, Any]) -> str:
        """
        Generate markdown content from note data.
        
        Args:
            note_data: Note data dictionary
            
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Title
        title = note_data.get('title', 'Untitled Note')
        lines.append(f"# {title}\n")
        
        # Metadata
        lines.append("---")
        lines.append(f"**Created:** {note_data.get('created_at', 'Unknown')}")
        lines.append(f"**Category:** {note_data.get('primary_tag', 'Other')}")
        lines.append(f"**Source:** {note_data.get('source', 'Unknown')}")
        
        # Tags
        secondary_tags = note_data.get('secondary_tags', [])
        if secondary_tags:
            tags_str = ", ".join(secondary_tags)
            lines.append(f"**Tags:** {tags_str}")
        
        lines.append("---\n")
        
        # Summary
        summary = note_data.get('summary')
        if summary:
            lines.append("## Summary")
            lines.append(f"{summary}\n")
        
        # Full Content
        lines.append("## Content")
        content = note_data.get('transcription') or note_data.get('original_text', '')
        lines.append(f"{content}\n")
        
        # Key Entities
        key_entities = note_data.get('key_entities', {})
        if any(key_entities.values()):
            lines.append("## Key Entities")
            
            if key_entities.get('people'):
                lines.append(f"**People:** {', '.join(key_entities['people'])}")
            
            if key_entities.get('places'):
                lines.append(f"**Places:** {', '.join(key_entities['places'])}")
            
            if key_entities.get('dates'):
                lines.append(f"**Dates:** {', '.join(key_entities['dates'])}")
            
            if key_entities.get('companies'):
                lines.append(f"**Companies:** {', '.join(key_entities['companies'])}")
            
            lines.append("")
        
        # Action Items
        action_items = note_data.get('actionable_items', [])
        if action_items:
            lines.append("## Action Items")
            for item in action_items:
                task = item.get('task', '')
                deadline = item.get('deadline', '')
                priority = item.get('priority', 'medium')
                
                line = f"- [ ] {task}"
                if deadline:
                    line += f" (Due: {deadline})"
                line += f" [Priority: {priority}]"
                lines.append(line)
            lines.append("")
        
        # Topics
        topics = note_data.get('topics', [])
        if topics:
            lines.append(f"**Topics:** {', '.join(topics)}")
        
        return "\n".join(lines)
    
    async def create_folder(
        self,
        folder_name: str,
        token_data: Dict[str, Any],
        parent_folder_id: Optional[str] = None
    ) -> str:
        """
        Create a folder in Google Drive.
        
        Args:
            folder_name: Name of the folder
            token_data: OAuth token data
            parent_folder_id: Parent folder ID (optional)
            
        Returns:
            Created folder ID
        """
        try:
            service = self.create_service(token_data)
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Folder created: {folder_name} ({folder_id})")
            
            return folder_id
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            raise
    
    async def list_files(
        self,
        token_data: Dict[str, Any],
        folder_id: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """
        List files in Google Drive.
        
        Args:
            token_data: OAuth token data
            folder_id: Folder ID to list (optional)
            limit: Maximum number of files to return
            
        Returns:
            List of files
        """
        try:
            service = self.create_service(token_data)
            
            query = ""
            if folder_id:
                query = f"'{folder_id}' in parents"
            
            results = service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id, name, webViewLink, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    async def delete_file(
        self,
        file_id: str,
        token_data: Dict[str, Any]
    ) -> bool:
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: File ID to delete
            token_data: OAuth token data
            
        Returns:
            True if successful
        """
        try:
            service = self.create_service(token_data)
            service.files().delete(fileId=file_id).execute()
            logger.info(f"File deleted: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def validate_token(self, token_data: Dict[str, Any]) -> bool:
        """
        Validate Google Drive token.
        
        Args:
            token_data: OAuth token data
            
        Returns:
            True if token is valid
        """
        try:
            service = self.create_service(token_data)
            # Try a simple API call
            service.files().list(pageSize=1).execute()
            return True
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False


# Global instance
gdrive_service = GDriveService()