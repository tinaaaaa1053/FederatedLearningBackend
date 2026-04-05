"""
Mock service implementation for testing without database
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.schemas.job import (
    JobResponse, JobDetailResponse, JobMetricsResponse, JobListRequest
)
from app.schemas.dashboard import DashboardStats, ClientInfo, CurrentJob, ChartData
from app.schemas.model import ModelResponse, ModelDetailResponse, ModelListRequest
from app.schemas.client import ClientResponse, ClientDetailResponse, ClientListRequest
from app.schemas.data_quality import QualityStats, QualityDistribution, NodeQuality, Warning
from app.schemas.settings import SettingsResponse, TestConnectionResponse, UserInfo
from app.schemas.common import PaginatedResponse
from app.utils.mock_data import (
    mock_jobs, mock_clients, mock_models, mock_data_quality, mock_settings
)


class MockJobService:
    """Mock job service for testing"""

    async def get_dashboard_stats(self) -> DashboardStats:
        """Get mock dashboard statistics"""
        return DashboardStats(
            activeJobs=2,
            completedJobs=3,
            totalClients=10,
            onlineClients=7
        )

    async def get_dashboard_clients(self) -> List[ClientInfo]:
        """Get mock dashboard clients"""
        return [
            ClientInfo(
                id=c["id"],
                name=c["name"],
                gpu=c["gpu"],
                status=c["status"]
            )
            for c in mock_clients if c["status"] == "online"
        ]

    async def get_current_job(self) -> Optional[CurrentJob]:
        """Get mock current job"""
        current_job = next((j for j in mock_jobs if j["status"] == "running"), None)
        if not current_job:
            return None

        progress = (current_job["current_round"] / current_job["total_rounds"] * 100)
        active_clients = len(current_job["client_ids"])

        return CurrentJob(
            jobId=current_job["id"],
            jobName=current_job["name"],
            progress=progress,
            currentRound=current_job["current_round"],
            totalRounds=current_job["total_rounds"],
            accuracy=current_job["accuracy"],
            loss=current_job["loss"],
            activeClients=active_clients,
            totalClients=len(current_job["client_ids"]),
            estimatedTimeRemaining="2小时"
        )

    async def get_realtime_logs(self) -> List[str]:
        """Get mock real-time logs"""
        return [
            "[INFO] System initialized",
            "[INFO] Waiting for jobs...",
            "[INFO] Job FL-2023-001 started",
            "[INFO] Round 1 completed - accuracy: 0.65, loss: 1.20"
        ]

    async def get_chart_data(self, chart_type: str) -> ChartData:
        """Get mock chart data"""
        job = mock_jobs[0]
        rounds = [str(i + 1) for i in range(len(job["metrics"]["accuracy"]))]

        return ChartData(
            rounds=rounds,
            accuracy=job["metrics"]["accuracy"] if chart_type == "accuracy" else None,
            loss=job["metrics"]["loss"] if chart_type == "loss" else None
        )

    async def get_job_list(
        self, page: int = 1, page_size: int = 10,
        status: Optional[str] = None, keyword: Optional[str] = None
    ) -> PaginatedResponse:
        """Get mock job list"""
        jobs = mock_jobs

        if status:
            jobs = [j for j in jobs if j["status"] == status]

        if keyword:
            jobs = [j for j in jobs if keyword.lower() in j["name"].lower()]

        total = len(jobs)
        start = (page - 1) * page_size
        end = start + page_size

        records = []
        for j in jobs[start:end]:
            records.append(JobResponse(
                id=j["id"],
                name=j["name"],
                description=j["description"],
                status=j["status"],
                jobType=j["job_type"],
                algorithm=j["algorithm"],
                currentRound=j["current_round"],
                totalRounds=j["total_rounds"],
                accuracy=j["accuracy"],
                loss=j["loss"],
                createdAt=j["created_at"],
                config=j["config"],
                clients=[
                    {
                        "id": c["id"],
                        "name": c["name"],
                        "status": c["status"],
                        "gpu": c["gpu"]
                    }
                    for c in mock_clients if c["id"] in j["client_ids"]
                ],
                metrics=j["metrics"]
            ))

        return PaginatedResponse(
            records=records,
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def get_job_detail(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get mock job detail"""
        job = next((j for j in mock_jobs if j["id"] == job_id), None)
        if not job:
            return None

        return {
            "id": job["id"],
            "name": job["name"],
            "description": job["description"],
            "status": job["status"],
            "jobType": job["job_type"],
            "algorithm": job["algorithm"],
            "currentRound": job["current_round"],
            "totalRounds": job["total_rounds"],
            "accuracy": job["accuracy"],
            "loss": job["loss"],
            "createdAt": job["created_at"],
            "startedAt": job["started_at"],
            "completedAt": job["completed_at"],
            "config": job["config"],
            "clients": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "status": c["status"],
                    "gpu": c["gpu"]
                }
                for c in mock_clients if c["id"] in job["client_ids"]
            ],
            "metrics": job["metrics"]
        }

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock job"""
        new_job = {
            "id": f"FL-2023-{len(mock_jobs) + 1:03d}",
            "name": job_data["name"],
            "description": job_data.get("description", ""),
            "status": "pending",
            "job_type": job_data.get("jobType", "custom"),
            "algorithm": job_data.get("algorithm", "FedAvg算法"),
            "current_round": 0,
            "total_rounds": job_data.get("totalRounds", 10),
            "accuracy": 0.0,
            "loss": 0.0,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "config": job_data.get("config", {}),
            "metrics": {
                "accuracy": [],
                "loss": [],
                "round_time": [],
                "train_loss": [],
                "test_loss": []
            },
            "client_ids": job_data.get("clientIds", [])
        }

        mock_jobs.append(new_job)
        return new_job

    async def abort_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Abort mock job"""
        job = next((j for j in mock_jobs if j["id"] == job_id), None)
        if not job:
            return None

        job["status"] = "aborted"
        job["completed_at"] = datetime.now()
        return job

    async def get_job_logs(self, job_id: str) -> Optional[str]:
        """Get mock job logs"""
        job = next((j for j in mock_jobs if j["id"] == job_id), None)
        if not job:
            return None

        logs = f"Job {job_id} logs\n"
        logs += f"Status: {job['status']}\n"
        logs += f"Current Round: {job['current_round']}/{job['total_rounds']}\n"
        return logs

    async def get_job_metrics(self, job_id: str) -> Optional[JobMetricsResponse]:
        """Get mock job metrics"""
        job = next((j for j in mock_jobs if j["id"] == job_id), None)
        if not job:
            return None

        metrics = job["metrics"]
        rounds = list(range(1, len(metrics["accuracy"]) + 1))

        return JobMetricsResponse(
            rounds=rounds,
            accuracy=metrics["accuracy"],
            loss=metrics["loss"],
            precision=metrics.get("precision", []),
            recall=metrics.get("recall", []),
            f1Score=metrics.get("f1Score", []),
            trainingTime=120.5
        )

    async def save_model_file(self, job_id: str, filename: str, content: bytes) -> dict:
        """Save uploaded model file"""
        return {"jobId": job_id, "modelFile": filename, "status": "saved"}

    async def update_job_progress(self, job_id: str, round_num: int, accuracy: float, loss: float) -> None:
        """Update job progress"""
        job = next((j for j in mock_jobs if j["id"] == job_id), None)
        if job:
            job["current_round"] = round_num
            job["accuracy"] = accuracy
            job["loss"] = loss
            job["metrics"]["accuracy"].append(accuracy)
            job["metrics"]["loss"].append(loss)


class MockModelService:
    """Mock model service for testing"""

    async def get_model_list(
        self, page: int = 1, page_size: int = 10,
        keyword: Optional[str] = None, job_id: Optional[str] = None
    ) -> PaginatedResponse:
        """Get mock model list"""
        models = mock_models

        if keyword:
            models = [m for m in models if keyword.lower() in m["name"].lower()]

        if job_id:
            models = [m for m in models if m["job_id"] == job_id]

        total = len(models)
        start = (page - 1) * page_size
        end = start + page_size

        records = []
        for m in models[start:end]:
            records.append(ModelResponse(
                id=m["id"],
                name=m["name"],
                jobId=m["job_id"],
                accuracy=m["accuracy"],
                loss=m["loss"],
                createdAt=m["createdAt"],
                framework=m["framework"],
                parameters=m["parameters"],
                size=m["size"],
                architecture=m["architecture"],
                dataset=m["dataset"],
                rounds=m["rounds"],
                clients=m["clients"],
                metrics=m["metrics"]
            ))

        return PaginatedResponse(
            records=records,
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def get_model_detail(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get mock model detail"""
        model = next((m for m in mock_models if m["id"] == model_id), None)
        if not model:
            return None

        return model

    async def upload_model(
        self, name: str, file_content: bytes, file_name: str,
        job_id: Optional[str] = None, framework: str = "PyTorch",
        architecture: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload mock model"""
        new_model = {
            "id": f"model-{len(mock_models) + 1}",
            "name": name,
            "job_id": job_id,
            "accuracy": 0.85,
            "loss": 0.28,
            "createdAt": datetime.now(),
            "framework": framework,
            "parameters": "25.6M",
            "size": "98.2 MB",
            "architecture": architecture or "ResNet-50",
            "dataset": "Medical Images",
            "rounds": 10,
            "clients": 8,
            "metrics": {
                "accuracy": [72, 78, 82, 85, 87, 89, 90, 91, 91.8, 92.4],
                "loss": [0.85, 0.72, 0.63, 0.55, 0.48, 0.42, 0.38, 0.34, 0.30, 0.28],
                "precision": [0.78, 0.82, 0.85, 0.87, 0.89, 0.91, 0.92, 0.93, 0.94, 0.95],
                "recall": [0.75, 0.79, 0.83, 0.86, 0.88, 0.90, 0.91, 0.92, 0.93, 0.94]
            }
        }

        mock_models.append(new_model)
        return new_model

    async def get_model_file(self, model_id: str) -> Optional[Tuple[bytes, str]]:
        """Get mock model file"""
        model = next((m for m in mock_models if m["id"] == model_id), None)
        if not model:
            return None

        # Return dummy file content
        return b"model weights data", f"{model_id}_model.pth"

    async def validate_model(self, model_id: str) -> Dict[str, Any]:
        """Validate mock model"""
        model = next((m for m in mock_models if m["id"] == model_id), None)
        if not model:
            return {"valid": False, "error": "Model not found"}

        return {
            "valid": True,
            "modelId": model_id,
            "framework": model["framework"],
            "architecture": model["architecture"]
        }

    async def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """Compare mock models"""
        models = [m for m in mock_models if m["id"] in model_ids]

        comparison_data = {}
        for model in models:
            comparison_data[model["id"]] = {
                "name": model["name"],
                "accuracy": model["accuracy"],
                "loss": model["loss"],
                "rounds": model["rounds"],
                "clients": model["clients"],
                "framework": model["framework"],
                "metrics": model["metrics"]
            }

        return {
            "modelIds": model_ids,
            "comparisonData": comparison_data
        }

    async def delete_model(self, model_id: str) -> bool:
        """Delete mock model"""
        model = next((m for m in mock_models if m["id"] == model_id), None)
        if not model:
            return False

        mock_models.remove(model)
        return True

    async def sync_from_storage_service(self, user_name: str) -> List[Dict[str, Any]]:
        """Sync models from storage service"""
        return []


class MockClientService:
    """Mock client service for testing"""

    async def get_client_list(
        self, page: int = 1, page_size: int = 10,
        status: Optional[str] = None, keyword: Optional[str] = None
    ) -> PaginatedResponse:
        """Get mock client list"""
        clients = mock_clients

        if status:
            clients = [c for c in clients if c["status"] == status]

        if keyword:
            clients = [c for c in clients if keyword.lower() in c["name"].lower()]

        total = len(clients)
        start = (page - 1) * page_size
        end = start + page_size

        records = []
        for c in clients[start:end]:
            records.append(ClientResponse(
                id=c["id"],
                name=c["name"],
                status=c["status"],
                connectedAt=c.get("connected_at"),
                jobCount=c.get("job_count", 0),
                gpu=c.get("gpu"),
                cpu=c.get("cpu"),
                memory=c.get("memory"),
                os=c.get("os"),
                ipAddress=c.get("ip_address"),
                port=c.get("port"),
                deviceType=c.get("device_type")
            ))

        return PaginatedResponse(
            records=records,
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def get_client_detail(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get mock client detail"""
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if not client:
            return None

        return client

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock client"""
        new_client = {
            "id": f"client-{len(mock_clients) + 1}",
            "name": client_data["name"],
            "device_type": client_data["deviceType"],
            "ip_address": client_data["ipAddress"],
            "port": client_data["port"],
            "fedlbe_port": client_data["fedlbePort"],
            "gpu": client_data["gpu"],
            "cpu": client_data["cpu"],
            "memory": client_data["memory"],
            "os": client_data["os"],
            "status": "offline",
            "device_info": {
                "type": client_data["deviceType"],
                "ipAddress": client_data["ipAddress"],
                "port": client_data["port"],
                "os": client_data["os"],
                "cpu": client_data["cpu"],
                "memory": client_data["memory"],
                "gpu": client_data["gpu"]
            },
            "resource_usage": {
                "cpuUsage": 0.0,
                "memoryUsage": 0.0,
                "diskUsage": 0.0,
                "networkIO": 0.0
            },
            "job_count": 0,
            "participated_jobs": [],
            "performance_metrics": {
                "days": 0,
                "trainingTime": 0.0,
                "dataTransfer": 0.0
            }
        }

        mock_clients.append(new_client)
        return new_client

    async def update_client(self, client_id: str, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update mock client"""
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if not client:
            return None

        update_data = client_data
        for field, value in update_data.items():
            if field == "deviceType" and value:
                client["device_type"] = value
            elif field in client:
                client[field] = value

        return client

    async def delete_client(self, client_id: str) -> bool:
        """Delete mock client"""
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if not client:
            return False

        mock_clients.remove(client)
        return True

    async def reconnect_client(self, client_id: str) -> bool:
        """Reconnect mock client"""
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if not client:
            return False

        client["status"] = "online"
        return True

    async def get_online_clients(self) -> List[Dict[str, Any]]:
        """Get mock online clients"""
        return [c for c in mock_clients if c["status"] == "online"]

    async def update_client_status(self, client_id: str, status, resource_usage: Optional[dict] = None) -> None:
        """Update client status"""
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if client:
            client["status"] = status.value if hasattr(status, 'value') else status

    async def update_client_job_participation(self, client_id: str, job_info: dict) -> None:
        """Update client job participation"""
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if client:
            if "participated_jobs" not in client:
                client["participated_jobs"] = []
            client["participated_jobs"].append(job_info)
            client["job_count"] = len(client["participated_jobs"])


class MockDataQualityService:
    """Mock data quality service for testing"""

    async def get_quality_stats(self) -> QualityStats:
        """Get mock quality stats"""
        return mock_data_quality["stats"]

    async def get_node_quality_data(self) -> List[NodeQuality]:
        """Get mock node quality data"""
        return mock_data_quality["nodes"]

    async def get_quality_distribution(self) -> QualityDistribution:
        """Get mock quality distribution"""
        return mock_data_quality["distribution"]

    async def get_warnings(
        self, page: int = 1, page_size: int = 10,
        warning_type: Optional[str] = None
    ) -> PaginatedResponse:
        """Get mock warnings"""
        warnings = mock_data_quality["warnings"]

        if warning_type:
            warnings = [w for w in warnings if w["type"] == warning_type]

        total = len(warnings)
        start = (page - 1) * page_size
        end = start + page_size

        records = []
        for w in warnings[start:end]:
            records.append(Warning(
                id=w["id"],
                type=w["type"],
                nodeId=w["nodeId"],
                title=w["title"],
                message=w["message"],
                timestamp=w["timestamp"]
            ))

        return PaginatedResponse(
            records=records,
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def generate_report(self) -> Optional[bytes]:
        """Generate mock report"""
        return b"Mock data quality report content"


class MockSettingsService:
    """Mock settings service for testing"""

    async def get_settings(self) -> SettingsResponse:
        """Get mock settings"""
        return mock_settings

    async def save_settings(self, settings_data: Dict[str, Any]) -> None:
        """Save mock settings"""
        # In mock mode, just update the mock data
        if hasattr(mock_settings, 'update'):
            for key, value in settings_data.items():
                if hasattr(mock_settings, key):
                    setattr(mock_settings, key, value)

    async def test_connection(self, request: Dict[str, Any]) -> TestConnectionResponse:
        """Test mock connection"""
        return TestConnectionResponse(
            status="connected",
            latency=15.2,
            version="1.0.0"
        )

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock user"""
        new_user = {
            "id": f"user-{len(mock_settings.users) + 1}",
            "username": user_data["username"],
            "role": user_data["role"],
            "status": "active",
            "email": user_data.get("email"),
            "fullName": user_data.get("fullName")
        }

        mock_settings.users.append(new_user)
        return new_user

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update mock user"""
        user = next((u for u in mock_settings.users if u["id"] == user_id), None)
        if not user:
            return None

        for field, value in user_data.items():
            if field in user:
                user[field] = value

        return user

    async def delete_user(self, user_id: str) -> bool:
        """Delete mock user"""
        user = next((u for u in mock_settings.users if u["id"] == user_id), None)
        if not user:
            return False

        mock_settings.users.remove(user)
        return True

    async def reset_settings(self) -> None:
        """Reset mock settings"""
        # Reset to original mock data
        pass