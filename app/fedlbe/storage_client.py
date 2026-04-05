"""
FedLBE Storage Service Client

This module provides REST client for communicating with FedLBE StorageService.
"""
import httpx
from typing import Optional, List, Dict, Any
from loguru import logger

from app.config import settings


class StorageServiceClient:
    """
    REST client for FedLBE StorageService.

    Handles:
    - Retrieving trained model weights
    - Fetching training results
    - Listing available tasks
    """

    def __init__(self, storage_url: str = None):
        self.storage_url = storage_url or settings.FEDLBE_STORAGE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_model_weights(
        self, user_name: str, task_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve trained model weights.

        Args:
            user_name: User identifier
            task_name: Task/job identifier

        Returns:
            Model weights data or None if not found
        """
        try:
            response = await self.client.post(
                f"{self.storage_url}/receive_weights",
                json={"user_name": user_name, "task_name": task_name}
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get model weights: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting model weights: {e}")
            return None

    async def get_training_results(
        self, user_name: str, task_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve training results/metrics.

        Args:
            user_name: User identifier
            task_name: Task/job identifier

        Returns:
            Training results data or None if not found
        """
        try:
            response = await self.client.post(
                f"{self.storage_url}/receive_data",
                json={"user_name": user_name, "task_name": task_name}
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get training results: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting training results: {e}")
            return None

    async def get_tasks(self, user_name: str) -> List[Dict[str, Any]]:
        """
        List all tasks for a user.

        Args:
            user_name: User identifier

        Returns:
            List of tasks
        """
        try:
            response = await self.client.post(
                f"{self.storage_url}/receive_tasks",
                json={"user_name": user_name}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("tasks", [])
            else:
                logger.warning(f"Failed to get tasks: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if StorageService is healthy"""
        try:
            response = await self.client.get(f"{self.storage_url}/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global instance
storage_client = StorageServiceClient()
