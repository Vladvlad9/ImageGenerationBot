import asyncio

from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.storage import Storage

from settings import settings
import logging

# 6a634bf00009d5dc1411

logger = logging.getLogger(__name__)

__all__ = ["StorageAppWrite"]


class StorageAppWrite:
    def __init__(self, bucket_id: str) -> None:
        self.bucket_id = bucket_id

        client = Client()
        client.set_endpoint(settings.STORAGE.ENDPOINT)
        client.set_project(settings.STORAGE.PROJECT)
        client.set_key(settings.STORAGE.KEY)

        self.storage = Storage(client)

    async def get_file_view(self, file_id: str) -> bytes:
        try:
            return await asyncio.to_thread(
                self.storage.get_file_view,
                bucket_id=self.bucket_id,
                file_id=file_id,
            )
        except AppwriteException:
            logger.exception(
                "Failed to get file view: bucket=%s, file=%s",
                self.bucket_id,
                file_id,
            )
            raise
