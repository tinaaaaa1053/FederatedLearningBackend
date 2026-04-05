"""
Client Management Service
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import SessionLocal
from app.models.client import Client, ClientStatus, DeviceType
from app.schemas.client import (
    ClientResponse, ClientDetailResponse, ClientCreate, ClientUpdate,
    DeviceInfo, ResourceUsage, ParticipatedJob, PerformanceMetrics
)
from app.schemas.common import PaginatedResponse


class ClientService:
    """Service for client management operations"""

    def __init__(self):
        self.db: Session = SessionLocal()

    def _client_to_response(self, client: Client) -> ClientResponse:
        """Convert Client to ClientResponse schema"""
        return ClientResponse(
            id=client.id,
            name=client.name,
            status=client.status.value,
            connectedAt=client.connected_at,
            jobCount=client.job_count,
            gpu=client.gpu,
            cpu=client.cpu,
            memory=client.memory,
            os=client.os,
            ipAddress=client.ip_address,
            port=client.port,
            deviceType=client.device_type.value if client.device_type else None
        )

    async def get_client_list(
        self, page: int = 1, page_size: int = 10,
        status: Optional[str] = None, keyword: Optional[str] = None
    ) -> PaginatedResponse[ClientResponse]:
        """Get paginated client list"""
        query = self.db.query(Client)

        if status:
            query = query.filter(Client.status == ClientStatus(status))

        if keyword:
            query = query.filter(
                or_(
                    Client.name.ilike(f"%{keyword}%"),
                    Client.id.ilike(f"%{keyword}%")
                )
            )

        total = query.count()
        clients = query.order_by(Client.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return PaginatedResponse(
            records=[self._client_to_response(c) for c in clients],
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def get_client_detail(self, client_id: str) -> Optional[ClientDetailResponse]:
        """Get client detail by ID"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None

        participated_jobs = []
        if client.participated_jobs:
            participated_jobs = [
                ParticipatedJob(**job) for job in client.participated_jobs
            ]

        return ClientDetailResponse(
            id=client.id,
            name=client.name,
            status=client.status.value,
            deviceType=client.device_type.value if client.device_type else None,
            connectedAt=client.connected_at,
            lastHeartbeat=client.last_heartbeat,
            jobCount=client.job_count,
            gpu=client.gpu,
            cpu=client.cpu,
            memory=client.memory,
            os=client.os,
            ipAddress=client.ip_address,
            port=client.port,
            deviceInfo=DeviceInfo(**client.device_info) if client.device_info else None,
            resourceUsage=ResourceUsage(**client.resource_usage) if client.resource_usage else None,
            participatedJobs=participated_jobs,
            performanceMetrics=PerformanceMetrics(**client.performance_metrics) if client.performance_metrics else None
        )

    async def create_client(self, client_data: ClientCreate) -> Client:
        """Create a new client"""
        client = Client(
            name=client_data.name,
            device_type=DeviceType(client_data.deviceType),
            ip_address=client_data.ipAddress,
            port=client_data.port,
            fedlbe_port=client_data.fedlbePort,
            gpu=client_data.gpu,
            cpu=client_data.cpu,
            memory=client_data.memory,
            os=client_data.os,
            status=ClientStatus.OFFLINE,
            device_info={
                "type": client_data.deviceType,
                "ipAddress": client_data.ipAddress,
                "port": client_data.port,
                "os": client_data.os,
                "cpu": client_data.cpu,
                "memory": client_data.memory,
                "gpu": client_data.gpu
            }
        )

        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)

        return client

    async def update_client(self, client_id: str, client_data: ClientUpdate) -> Optional[Client]:
        """Update client information"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None

        update_data = client_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "deviceType" and value:
                client.device_type = DeviceType(value)
            elif hasattr(client, field):
                setattr(client, field, value)

        self.db.commit()
        self.db.refresh(client)

        return client

    async def delete_client(self, client_id: str) -> bool:
        """Delete a client"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return False

        self.db.delete(client)
        self.db.commit()
        return True

    async def reconnect_client(self, client_id: str) -> bool:
        """Trigger client reconnection"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return False

        # TODO: Implement actual reconnection logic via FedLBE
        # This would typically involve sending a reconnection request to the client

        return True

    async def get_online_clients(self) -> List[dict]:
        """Get list of online clients"""
        clients = self.db.query(Client).filter(
            Client.status == ClientStatus.ONLINE
        ).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status.value,
                "ipAddress": c.ip_address
            }
            for c in clients
        ]

    async def update_client_status(
        self, client_id: str, status: ClientStatus,
        resource_usage: Optional[dict] = None
    ) -> None:
        """Update client status (called by FedLBE bridge)"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if client:
            client.status = status
            client.last_heartbeat = datetime.utcnow()

            if status == ClientStatus.ONLINE and not client.connected_at:
                client.connected_at = datetime.utcnow()

            if resource_usage:
                client.resource_usage = resource_usage

            self.db.commit()

    async def update_client_job_participation(
        self, client_id: str, job_info: dict
    ) -> None:
        """Update client's participated jobs"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if client:
            if not client.participated_jobs:
                client.participated_jobs = []

            client.participated_jobs.append(job_info)
            client.job_count = len(client.participated_jobs)
            self.db.commit()
