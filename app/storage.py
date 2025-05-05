import os
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import Storage, FileSystemStorage
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured
import requests

logger = logging.getLogger(__name__)

class VercelBlobStorage(Storage):
    """
    Custom storage backend for Vercel Blob storage
    Falls back to FileSystemStorage if not configured properly for local development
    """
    def __init__(self):
        self.token = os.getenv('BLOB_READ_WRITE_TOKEN')
        self.base_url = os.getenv('BLOB_BASE_URL', 'https://hg2cdq8jxv2osfar.public.blob.vercel-storage.com')
        self.folder = 'profile_pics'  # Folder for profile pictures
        
        # Use FileSystemStorage as fallback for local development
        if not self.token:
            logger.warning("BLOB_READ_WRITE_TOKEN not found. Using FileSystemStorage as fallback.")
            self.fallback = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'media'))
            self.using_fallback = True
        else:
            self.using_fallback = False
            
            # Import vercel_blob only if we're using it (avoids import errors in local dev)
            try:
                from vercel_blob import put, head, delete
                self.blob_put = put
                self.blob_head = head
                self.blob_delete = delete
            except ImportError:
                logger.error("Failed to import vercel_blob module. Falling back to FileSystemStorage.")
                self.fallback = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'media'))
                self.using_fallback = True

    def _save(self, name, content):
        if self.using_fallback:
            logger.info(f"Using FileSystemStorage fallback to save {name}")
            return self.fallback._save(name, content)
            
        try:
            logger.info(f"Attempting to upload {name} to Vercel Blob")
            file_name = os.path.join(self.folder, os.path.basename(name))
            
            blob = self.blob_put(
                file_name,
                content.file,
                {'access': 'public', 'token': self.token}
            )
            logger.info(f"Uploaded file to Vercel Blob: {blob['url']}")
            return file_name
        except Exception as e:
            logger.error(f"Failed to upload to Vercel Blob: {str(e)}")
            # Fall back to FileSystemStorage if Vercel upload fails
            if not hasattr(self, 'fallback'):
                self.fallback = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'media'))
            return self.fallback._save(name, content)

    def _open(self, name, mode='rb'):
        if self.using_fallback:
            return self.fallback._open(name, mode)
            
        try:
            blob_url = self.url(name)
            logger.info(f"Fetching file from Vercel Blob: {blob_url}")
            response = requests.get(blob_url)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            logger.error(f"Failed to open file from Vercel Blob: {str(e)}")
            if hasattr(self, 'fallback'):
                return self.fallback._open(name, mode)
            raise

    def exists(self, name):
        if self.using_fallback:
            return self.fallback.exists(name)
            
        try:
            file_name = os.path.join(self.folder, os.path.basename(name))
            self.blob_head(file_name, token=self.token)
            return True
        except Exception:
            if hasattr(self, 'fallback'):
                return self.fallback.exists(name)
            return False

    def url(self, name):
        if self.using_fallback:
            return self.fallback.url(name)
            
        # Handle both full paths and relative paths
        file_name = os.path.basename(name)
        return urljoin(self.base_url, f"{self.folder}/{file_name}")

    def delete(self, name):
        if self.using_fallback:
            return self.fallback.delete(name)
            
        try:
            file_name = os.path.join(self.folder, os.path.basename(name))
            self.blob_delete(file_name, token=self.token)
            logger.info(f"Deleted file from Vercel Blob: {file_name}")
        except Exception as e:
            logger.error(f"Failed to delete file from Vercel Blob: {str(e)}")
            if hasattr(self, 'fallback'):
                return self.fallback.delete(name)
            raise

    def get_available_name(self, name, max_length=None):
        if self.using_fallback:
            return self.fallback.get_available_name(name, max_length)
        return super().get_available_name(name, max_length)