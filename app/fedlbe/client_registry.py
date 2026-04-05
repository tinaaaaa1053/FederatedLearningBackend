"""
FedLBE Client Registry

Tracks and manages connected FedLBE clients.
"""
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from loguru import logger

from app.services.client_service import ClientService
from app.models.client import ClientStatus


class ClientRegistry:
    """
    Registry for FedLBE clients.

    Responsibilities:
    - Track client connections
    - Monitor client health
    - Update client status in database
    """

    def __init__(self):
        self.clients: Dict[str, Dict] = {}  # client_id -> client info
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.heartbeat_interval = 30  # seconds

    async def start(self):
        """Start the client registry"""
        self._heartbeat_task = asyncio.create_task(self._check_heartbeats())
        logger.info("ClientRegistry started")

    async def stop(self):
        """Stop the client registry"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        logger.info("ClientRegistry stopped")

    async def _check_heartbeats(self):
        """Periodically check client heartbeats"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                service = ClientService()
                now = datetime.utcnow()

                for client_id, info in list(self.clients.items()):
                    last_heartbeat = info.get("last_heartbeat")
                    if last_heartbeat:
                        # If no heartbeat for 2x interval, mark as offline
                        elapsed = (now - last_heartbeat).total_seconds()
                        if elapsed > self.heartbeat_interval * 2:
                            await service.update_client_status(
                                client_id,
                                ClientStatus.OFFLINE
                            )
                            info["status"] = "offline"

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error checking heartbeats: {e}")

    def register_client(
        self, client_id: str, ip_address: str, port: int, **kwargs
    ):
        """Register a new client"""
        self.clients[client_id] = {
            "client_id": client_id,
            "ip_address": ip_address,
            "port": port,
            "status": "online",
            "registered_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow(),
            **kwargs
        }
        logger.info(f"Registered client {client_id} at {ip_address}:{port}")

    def unregister_client(self, client_id: str):
        """Unregister a client"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Unregistered client {client_id}")

    def update_heartbeat(self, client_id: str, resource_usage: Optional[Dict] = None):
        """Update client heartbeat"""
        if client_id in self.clients:
            self.clients[client_id]["last_heartbeat"] = datetime.utcnow()
            self.clients[client_id]["status"] = "online"

            if resource_usage:
                self.clients[client_id]["resource_usage"] = resource_usage

    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client info"""
        return self.clients.get(client_id)

    def get_all_clients(self) -> List[Dict]:
        """Get all registered clients"""
        return list(self.clients.values())

    def get_online_clients(self) -> List[Dict]:
        """Get all online clients"""
        return [
            c for c in self.clients.values()
            if c.get("status") == "online"
        ]

    async def select_clients(
        self, strategy: str, num_clients: int
    ) -> List[str]:
        """
        Select clients for a job.

        Args:
            strategy: Selection strategy (random, round_robin, latency, full)
            num_clients: Number of clients to select

        Returns:
            List of selected client IDs
        """
        online_clients = self.get_online_clients()

        if not online_clients:
            return []

        if strategy == "full":
            return [c["client_id"] for c in online_clients]

        if strategy == "random":
            import random
            selected = random.sample(
                online_clients,
                min(num_clients, len(online_clients))
            )
            return [c["client_id"] for c in selected]

        if strategy == "round_robin":
            # Simple round-robin selection
            start_idx = len(online_clients) % num_clients
            selected = online_clients[start_idx:start_idx + num_clients]
            return [c["client_id"] for c in selected]

        if strategy == "latency":
            # Sort by latency (lowest first)
            sorted_clients = sorted(
                online_clients,
                key=lambda c: c.get("latency", float("inf"))
            )
            selected = sorted_clients[:num_clients]
            return [c["client_id"] for c in selected]

        # Default: return all available
        return [c["client_id"] for c in online_clients[:num_clients]]


# Global instance
client_registry = ClientRegistry()
