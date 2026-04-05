"""
FedLBE Job Manager

Manages job state synchronization between FastAPI backend and FedLBE.
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime
from loguru import logger

from app.fedlbe.ws_client import fedlbe_bridge
from app.fedlbe.storage_client import storage_client
from app.services.job_service import JobService
from app.models.job import JobStatus


class JobManager:
    """
    Manages federated learning jobs.

    Responsibilities:
    - Submit jobs to FedLBE
    - Track job state
    - Sync results from StorageService
    """

    def __init__(self):
        self.jobs: Dict[str, Dict] = {}  # job_id -> job state
        self._sync_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the job manager"""
        # Connect to FedLBE
        await fedlbe_bridge.connect()

        # Start periodic sync
        self._sync_task = asyncio.create_task(self._periodic_sync())

        logger.info("JobManager started")

    async def stop(self):
        """Stop the job manager"""
        if self._sync_task:
            self._sync_task.cancel()

        await fedlbe_bridge.disconnect()
        await storage_client.close()

        logger.info("JobManager stopped")

    async def _periodic_sync(self):
        """Periodically sync job states with FedLBE"""
        while True:
            try:
                await asyncio.sleep(10)  # Sync every 10 seconds

                # Sync running jobs
                service = JobService()
                # TODO: Get running jobs and sync their state

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}")

    async def submit_job(self, job_id: str, job_data: Dict) -> bool:
        """
        Submit a job to FedLBE.

        Args:
            job_id: Internal job ID
            job_data: Job configuration

        Returns:
            True if submitted successfully
        """
        try:
            # Track job state
            self.jobs[job_id] = {
                "status": "submitting",
                "submitted_at": datetime.utcnow(),
                "job_data": job_data
            }

            # Submit to FedLBE
            fedlbe_job_id = await fedlbe_bridge.submit_job({
                "job_id": job_id,
                **job_data
            })

            # Update state
            self.jobs[job_id]["status"] = "running"
            self.jobs[job_id]["fedlbe_job_id"] = fedlbe_job_id

            return True

        except Exception as e:
            logger.error(f"Failed to submit job {job_id}: {e}")
            self.jobs[job_id]["status"] = "failed"
            return False

    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get current job status"""
        return self.jobs.get(job_id)

    async def sync_results(self, job_id: str, user_name: str = "default"):
        """
        Sync job results from StorageService.

        Args:
            job_id: Job ID
            user_name: User identifier
        """
        try:
            # Get results from StorageService
            results = await storage_client.get_training_results(user_name, job_id)

            if results:
                # Update job in database
                service = JobService()
                # TODO: Update job metrics from results

                logger.info(f"Synced results for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to sync results for job {job_id}: {e}")


# Global instance
job_manager = JobManager()
