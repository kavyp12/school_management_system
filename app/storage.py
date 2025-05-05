import os
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.core.exceptions import ImproperlyConfigured
from vercel_blob import put, head, delete
import logging
import requests

logger = logging.getLogger(__name__)

class VercelBlobStorage(Storage):
    def __init__(self):
        self.token = os.getenv('BLOB_READ_WRITE_TOKEN')
        if not self.token:
            raise ImproperlyConfigured("BLOB_READ_WRITE_TOKEN environment variable is not set.")
        self.base_url = 'https://your-blob-store.public.blob.vercel-storage.com'  # Replace with your Vercel Blob store URL
        self.folder = 'profile_pics'  # Folder for profile pictures

    def _save(self, name, content):
        try:
            file_name = os.path.join(self.folder, name)
            blob = put(
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
        from io import BytesIO
        try:
            blob_url = self.url(name)
            response = requests.get(blob_url)
            response.raise_for_status()
            return ContentFile(response.content)
        except Exception as e:
            logger.error(f"Failed to open file from Vercel Blob: {str(e)}")
            raise

    def exists(self, name):
        try:
            file_name = os.path.join(self.folder, name)
            head(file_name, token=self.token)
            return True
        except Exception:
            return False

    def url(self, name):
        file_name = os.path.join(self.folder, name)
        return f"{self.base_url}/{file_name}"

    def delete(self, name):
        try:
            file_name = os.path.join(self.folder, name)
            delete(file_name, token=self.token)
            logger.info(f"Deleted file from Vercel Blob: {file_name}")
        except Exception as e:
            logger.error(f"Failed to delete file from Vercel Blob: {str(e)}")
            raise

    def get_valid_name(self, name):
        return super().get_valid_name(name)

    def get_available_name(self, name, max_length=None):
        return super().get_available_name(name, max_length)