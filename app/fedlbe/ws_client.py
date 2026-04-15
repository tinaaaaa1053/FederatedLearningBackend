"""
FedLBE WebSocket Client Bridge

This module provides WebSocket client for communicating with FedLBE Server.
"""
import asyncio
import pickle
from typing import Optional, Callable, Dict, Any
import websockets
from bson import dumps as bson_encode

from app.config import settings
from loguru import logger


class FedLBEBridge:
    """
    WebSocket client bridge to FedLBE Server.

    Handles:
    - Job submission to FedLBE
    - Receiving training progress updates
    - Client status monitoring
    """

    def __init__(self, server_url: str = None):
        self.server_url = server_url or getattr(
            settings, "FEDLBE_SERVER_URL", settings.FEDLBE_WS_URL
        )
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.reconnect_interval = 5
        self.job_callbacks: Dict[str, Callable] = {}
        self._listener_task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """Connect to FedLBE Server"""
        try:
            self.ws = await websockets.connect(
                f"{self.server_url}/job_receive",
                ping_interval=20,
                ping_timeout=10
            )
            self.is_connected = True
            logger.info(f"Connected to FedLBE Server at {self.server_url}")

            # Start message listener
            self._listener_task = asyncio.create_task(self._listen_for_messages())

            return True
        except Exception as e:
            logger.error(f"Failed to connect to FedLBE Server: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Disconnect from FedLBE Server"""
        if self._listener_task:
            self._listener_task.cancel()
        if self.ws:
            await self.ws.close()
        self.is_connected = False
        logger.info("Disconnected from FedLBE Server")

    async def _listen_for_messages(self):
        """Listen for messages from FedLBE Server"""
        try:
            async for message in self.ws:
                try:
                    # FedLBE sends pickle-encoded results
                    result = pickle.loads(message)
                    await self._handle_message(result)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection to FedLBE Server closed")
            self.is_connected = False
            # Attempt reconnection
            await self._reconnect()
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            self.is_connected = False

    async def _reconnect(self):
        """Attempt to reconnect to FedLBE Server"""
        while not self.is_connected:
            logger.info(f"Attempting to reconnect in {self.reconnect_interval}s...")
            await asyncio.sleep(self.reconnect_interval)

            if await self.connect():
                logger.info("Reconnected to FedLBE Server")
                break

    async def _handle_message(self, result: Dict[str, Any]):
        """Handle incoming message from FedLBE"""
        status = result.get("status")

        if status == "results":
            # Training completed
            await self._handle_job_completion(result)
        elif status == "round_complete":
            # Round completed
            await self._handle_round_update(result)
        elif status == "error":
            # Error occurred
            await self._handle_error(result)
        else:
            logger.debug(f"Received message with status: {status}")

    async def _handle_job_completion(self, result: Dict[str, Any]):
        """Handle job completion notification"""
        job_id = result.get("job_id")
        logger.info(f"Job {job_id} completed")

        # Update job in database
        from app.services.job_service import JobService
        service = JobService()
        # Job is completed - update status

        # Notify callback if registered
        if job_id in self.job_callbacks:
            await self.job_callbacks[job_id](result)

    async def _handle_round_update(self, result: Dict[str, Any]):
        """Handle round completion update"""
        job_id = result.get("job_id")
        round_num = result.get("round", 0)
        accuracy = result.get("accuracy", 0)
        loss = result.get("loss", 0)

        logger.info(f"Job {job_id} round {round_num}: accuracy={accuracy}, loss={loss}")

        # Update job progress in database
        from app.services.job_service import JobService
        service = JobService()
        await service.update_job_progress(job_id, round_num, accuracy, loss)

    async def _handle_error(self, result: Dict[str, Any]):
        """Handle error notification"""
        job_id = result.get("job_id")
        error = result.get("error", "Unknown error")
        logger.error(f"Job {job_id} error: {error}")

    async def submit_job(self, job_data: Dict[str, Any]) -> str:
        """
        Submit a federated learning job to FedLBE Server.

        Args:
            job_data: Job configuration including:
                - job_id: Our internal job ID
                - comRounds: Number of communication rounds
                - clientFraction: Fraction of clients per round
                - epoch: Local training epochs
                - lr: Learning rate
                - minibatch: Batch size
                - scheduler: Client selection strategy
                - modelFile: Model file bytes
                - modelName: Model class name
                - dataset: Dataset name

        Returns:
            job_id: The submitted job ID
        """
        if not self.is_connected:
            await self.connect()

        # Prepare FedLBE job format
        fedlbe_job = {
            "comRounds": job_data.get("total_rounds", 10),
            "clientFraction": job_data.get("client_fraction", 1.0),
            "epoch": job_data.get("local_epochs", 5),
            "lr": job_data.get("learning_rate", 0.001),
            "minibatch": job_data.get("batch_size", 32),
            "scheduler": job_data.get("scheduler", "random"),
            "modelFile": job_data.get("model_file_bytes"),
            "modelName": job_data.get("model_class_name"),
            "dataset": job_data.get("dataset"),
            "compress": job_data.get("compression"),
        }

        # Encode as BSON
        message = bson_encode(fedlbe_job)

        # Send to FedLBE
        await self.ws.send(message)
        logger.info(f"Submitted job {job_data.get('job_id')} to FedLBE")

        return job_data.get("job_id")

    async def submit_hetero_job(self, job_data: Dict[str, Any]) -> str:
        """Submit a heterogeneous FL job to FedLBE Server"""
        if not self.is_connected:
            await self.connect()

        # Connect to hetero endpoint
        ws = await websockets.connect(f"{self.server_url}/job_receive_hetero")

        # Prepare job data for heterogeneous FL
        fedlbe_job = {
            **job_data,
            # Additional hetero-specific fields
        }

        message = bson_encode(fedlbe_job)
        await ws.send(message)

        return job_data.get("job_id")

    async def submit_llm_job(self, job_data: Dict[str, Any]) -> str:
        """Submit an LLM-orchestrated FL job to FedLBE Server"""
        if not self.is_connected:
            await self.connect()

        # Connect to LLM endpoint
        ws = await websockets.connect(f"{self.server_url}/job_receive_llm")

        # Prepare job data for LLM-orchestrated FL
        fedlbe_job = {
            **job_data,
            "prompt": job_data.get("prompt"),
        }

        message = bson_encode(fedlbe_job)
        await ws.send(message)

        return job_data.get("job_id")

    async def abort_job(self, job_id: str) -> bool:
        """Abort a running job"""
        # TODO: Implement job abort via FedLBE
        logger.info(f"Aborting job {job_id}")
        return True

    async def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """Get client status from FedLBE"""
        # TODO: Implement client status query
        return {"client_id": client_id, "status": "unknown"}

    def register_callback(self, job_id: str, callback: Callable):
        """Register a callback for job completion"""
        self.job_callbacks[job_id] = callback

    def unregister_callback(self, job_id: str):
        """Unregister a callback"""
        if job_id in self.job_callbacks:
            del self.job_callbacks[job_id]


# Global instance
fedlbe_bridge = FedLBEBridge()
