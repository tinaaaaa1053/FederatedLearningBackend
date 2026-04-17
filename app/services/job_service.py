"""
Job Management Service
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import SessionLocal
from app.models.job import Job, JobStatus, JobType, Algorithm
from app.models.client import Client, ClientStatus
from app.schemas.job import (
    JobCreate, JobResponse, JobDetailResponse,
    JobMetrics, JobClient, JobMetricsResponse
)
from app.schemas.dashboard import DashboardStats, ClientInfo, CurrentJob, ChartData
from app.schemas.common import PaginatedResponse
from app.fedlbe.ws_client import FedLBEBridge


class JobService:
    """Service for job management operations"""

    def __init__(self):
        self.db: Session = SessionLocal()
        self.fedlbe_bridge = FedLBEBridge()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def _job_to_response(self, job: Job) -> JobResponse:
        """Convert Job model to JobResponse schema"""
        clients = []
        if job.client_ids:
            for client_id in job.client_ids:
                client = self.db.query(Client).filter(Client.id == client_id).first()
                if client:
                    clients.append(JobClient(
                        id=client.id,
                        name=client.name,
                        status=client.status.value,
                        gpu=client.gpu
                    ))

        return JobResponse(
            id=job.id,
            name=job.name,
            description=job.description,
            status=job.status.value,
            type=job.job_type.value,
            jobType=job.job_type.value,
            algorithm=job.algorithm.value,
            currentRound=job.current_round,
            totalRounds=job.total_rounds,
            accuracy=job.accuracy or 0.0,
            loss=job.loss or 0.0,
            createdAt=job.created_at,
            config=job.config,
            clients=clients,
            metrics=JobMetrics(**job.metrics) if job.metrics else None
        )

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics"""
        active_jobs = self.db.query(Job).filter(
            Job.status == JobStatus.RUNNING
        ).count()

        completed_jobs = self.db.query(Job).filter(
            Job.status == JobStatus.COMPLETED
        ).count()

        total_clients = self.db.query(Client).count()
        online_clients = self.db.query(Client).filter(
            Client.status == ClientStatus.ONLINE
        ).count()

        return DashboardStats(
            activeJobs=active_jobs,
            completedJobs=completed_jobs,
            totalClients=total_clients,
            onlineClients=online_clients
        )

    async def get_dashboard_clients(self) -> List[ClientInfo]:
        """Get connected clients for dashboard"""
        clients = self.db.query(Client).filter(
            Client.status == ClientStatus.ONLINE
        ).limit(10).all()

        return [
            ClientInfo(
                id=c.id,
                name=c.name,
                gpu=c.gpu,
                status=c.status.value
            )
            for c in clients
        ]

    async def get_current_job(self) -> Optional[CurrentJob]:
        """Get currently running job"""
        job = self.db.query(Job).filter(
            Job.status == JobStatus.RUNNING
        ).first()

        if not job:
            return None

        progress = (job.current_round / job.total_rounds * 100) if job.total_rounds > 0 else 0
        active_clients = len([c for c in (job.client_ids or [])])

        return CurrentJob(
            jobId=job.id,
            jobName=job.name,
            progress=progress,
            currentRound=job.current_round,
            totalRounds=job.total_rounds,
            accuracy=job.accuracy or 0.0,
            loss=job.loss or 0.0,
            activeClients=active_clients,
            totalClients=len(job.client_ids or []),
            estimatedTimeRemaining=None  # TODO: Calculate based on round time
        )

    async def get_realtime_logs(self) -> List[str]:
        """Get real-time logs"""
        # TODO: Implement log streaming from FedLBE
        return ["[INFO] System initialized", "[INFO] Waiting for jobs..."]

    async def get_chart_data(self, chart_type: str) -> ChartData:
        """Get chart data for visualization"""
        job = self.db.query(Job).filter(
            Job.status.in_([JobStatus.RUNNING, JobStatus.COMPLETED])
        ).order_by(Job.created_at.desc()).first()

        if not job or not job.metrics:
            return ChartData(rounds=[], accuracy=[], loss=[])

        metrics = job.metrics
        rounds = [str(i + 1) for i in range(len(metrics.get("accuracy", [])))]

        return ChartData(
            rounds=rounds,
            accuracy=metrics.get("accuracy", []) if chart_type == "accuracy" else None,
            loss=metrics.get("loss", []) if chart_type == "loss" else None
        )

    async def get_job_list(
        self, page: int = 1, page_size: int = 10,
        status: Optional[str] = None, keyword: Optional[str] = None
    ) -> PaginatedResponse[JobResponse]:
        """Get paginated job list"""
        query = self.db.query(Job)

        if status:
            query = query.filter(Job.status == JobStatus(status))

        if keyword:
            query = query.filter(
                or_(
                    Job.name.ilike(f"%{keyword}%"),
                    Job.id.ilike(f"%{keyword}%")
                )
            )

        total = query.count()
        jobs = query.order_by(Job.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return PaginatedResponse(
            records=[self._job_to_response(j) for j in jobs],
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def get_job_detail(self, job_id: str) -> Optional[JobDetailResponse]:
        """Get job detail by ID"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        clients = []
        if job.client_ids:
            for client_id in job.client_ids:
                client = self.db.query(Client).filter(Client.id == client_id).first()
                if client:
                    clients.append(JobClient(
                        id=client.id,
                        name=client.name,
                        status=client.status.value,
                        gpu=client.gpu
                    ))

        return JobDetailResponse(
            id=job.id,
            name=job.name,
            description=job.description,
            status=job.status.value,
            type=job.job_type.value,
            jobType=job.job_type.value,
            algorithm=job.algorithm.value,
            currentRound=job.current_round,
            totalRounds=job.total_rounds,
            accuracy=job.accuracy or 0.0,
            loss=job.loss or 0.0,
            createdAt=job.created_at,
            startedAt=job.started_at,
            completedAt=job.completed_at,
            config=job.config,
            clients=clients,
            metrics=JobMetrics(**job.metrics) if job.metrics else None
        )

    async def create_job(self, job_data: JobCreate) -> Job:
        """Create new job"""
        job = Job(
            name=job_data.name,
            description=job_data.description,
            job_type=JobType(job_data.jobType.lower()),
            algorithm=Algorithm(job_data.algorithm),
            total_rounds=job_data.totalRounds,
            config=job_data.config.model_dump(),
            client_ids=job_data.clientIds,
            status=JobStatus.PENDING
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # TODO: Submit job to FedLBE
        # await self.fedlbe_bridge.submit_job(job)

        return job

    async def abort_job(self, job_id: str) -> Optional[Job]:
        """Abort a running job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        if job.status == JobStatus.RUNNING:
            job.status = JobStatus.ABORTED
            job.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(job)

            # TODO: Notify FedLBE to stop the job

        return job

    async def get_job_logs(self, job_id: str) -> Optional[str]:
        """Get job logs"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        # TODO: Fetch actual logs from FedLBE
        logs = f"Job {job_id} logs\n"
        logs += f"Status: {job.status}\n"
        logs += f"Current Round: {job.current_round}/{job.total_rounds}\n"

        return logs

    async def get_job_metrics(self, job_id: str) -> Optional[JobMetricsResponse]:
        """Get job metrics"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        metrics = job.metrics or {}
        rounds = list(range(1, len(metrics.get("accuracy", [])) + 1))

        return JobMetricsResponse(
            rounds=rounds,
            accuracy=metrics.get("accuracy", []),
            loss=metrics.get("loss", []),
            precision=metrics.get("precision", []),
            recall=metrics.get("recall", []),
            f1Score=metrics.get("f1Score", []),
            trainingTime=0.0  # TODO: Calculate total training time
        )

    async def save_model_file(self, job_id: str, filename: str, content: bytes) -> dict:
        """Save uploaded model file"""
        import os
        from app.config import settings

        # Create models directory if not exists
        models_dir = os.path.join(os.getcwd(), "uploaded_models")
        os.makedirs(models_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(models_dir, f"{job_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        # Update job with model file path
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.model_file_path = file_path
            self.db.commit()

        return {"jobId": job_id, "modelFile": filename, "status": "saved"}

    async def update_job_progress(
        self, job_id: str, round_num: int,
        accuracy: float, loss: float
    ) -> None:
        """Update job progress (called by FedLBE bridge)"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.current_round = round_num
            job.accuracy = accuracy
            job.loss = loss

            # Update metrics history
            if not job.metrics:
                job.metrics = {"accuracy": [], "loss": []}
            job.metrics["accuracy"].append(accuracy)
            job.metrics["loss"].append(loss)

            self.db.commit()
