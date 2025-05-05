import os
import logging
from urllib.parse import urljoin
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured
import requests

logger = logging.getLogger(__name__)

class VercelBlobStorage(Storage):
    """
    Custom storage backend for Vercel Blob storage
    """
    def __init__(self):
        self.token = os.getenv('BLOB_READ_WRITE_TOKEN')
        if not self.token:
            raise ImproperlyConfigured("BLOB_READ_WRITE_TOKEN environment variable is not set.")
        
        self.base_url = os.getenv('BLOB_BASE_URL', 'https://hg2cdq8jxv2osfar.public.blob.vercel-storage.com')
        self.folder = 'profile_pics'  # Folder for profile pictures
        
        # Import vercel_blob
        try:
            from vercel_blob import put, head, delete
            self.blob_put = put
            self.blob_head = head
            self.blob_delete = delete
        except ImportError as e:
            logger.error(f"Failed to import vercel_blob module: {str(e)}")
            raise ImproperlyConfigured("vercel_blob module is not installed. Ensure it is included in requirements.txt.")

    def _save(self, name, content):
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
            raise

    def _open(self, name, mode='rb'):
        try:
            blob_url = self.url(name)
            logger.info(f"Fetching file from Vercel Blob: {blob_url}")
            response = requests.get(blob_url)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            logger.error(f"Failed to open file from Vercel Blob: {str(e)}")
            raise

    def exists(self, name):
        try:
            file_name = os.path.join(self.folder, os.path.basename(name))
            self.blob_head(file_name, token=self.token)
            return True
        except Exception:
            return False

    def url(self, name):
        file_name = os.path.basename(name)
        return urljoin(self.base_url, f"{self.folder}/{file_name}")

    def delete(self, name):
        try:
            file_name = os.path.join(self.folder, os.path.basename(name))
            self.blob_delete(file_name, token=self.token)
            logger.info(f"Deleted file from Vercel Blob: {file_name}")
        except Exception as e:
            logger.error(f"Failed to delete file from Vercel Blob: {str(e)}")
            raise

    def get_available_name(self, name, max_length=None):
        return super().get_available_name(name, max_length)