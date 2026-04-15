"""
Mock data generation utilities for testing without database
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.schemas.job import JobResponse, JobClient, JobMetrics
from app.schemas.dashboard import DashboardStats, ClientInfo, CurrentJob, ChartData
from app.schemas.model import ModelResponse, ModelMetrics
from app.schemas.client import ClientResponse, DeviceInfo, ResourceUsage, ParticipatedJob, PerformanceMetrics
from app.schemas.data_quality import QualityStats, QualityDistribution, NodeQuality, Warning
from app.schemas.settings import ConnectionSettings, WorkspaceSettings, SecuritySettings, UserInfo


def is_mock_mode() -> bool:
    """Check if mock mode is enabled"""
    # In a real implementation, this could check an environment variable
    return True


def generate_mock_jobs() -> List[Dict[str, Any]]:
    """Generate mock job data"""
    jobs = []
    for i in range(1, 6):
        rounds = 10
        current_round = i * 2
        accuracy = 0.65 + (i * 0.05)
        loss = 1.2 - (i * 0.1)

        jobs.append({
            "id": f"FL-2023-{i:03d}",
            "name": f"医学图像分割任务 {i}",
            "description": f"使用联邦学习进行医学图像分割的第 {i} 个任务",
            "status": "running" if i % 2 == 0 else "completed",
            "job_type": "medical",
            "algorithm": "FedAvg算法",
            "current_round": current_round,
            "total_rounds": rounds,
            "accuracy": accuracy,
            "loss": loss,
            "created_at": datetime.now() - timedelta(days=i),
            "started_at": datetime.now() - timedelta(days=i, hours=i*2),
            "completed_at": None if i % 2 == 0 else datetime.now() - timedelta(days=i-1),
            "config": {
                "modelArchitecture": "ResNet-50",
                "framework": "PyTorch",
                "dataset": "Medical Images",
                "batchSize": 32,
                "learningRate": 0.001,
                "optimizer": "Adam",
                "lossFunction": "CrossEntropy",
                "clients": 8,
                "minClients": 5,
                "maxClients": 8,
                "secureComm": True,
                "secureAgg": True,
                "differentialPrivacy": False
            },
            "metrics": {
                "accuracy": [0.65, 0.68, 0.71, 0.73, 0.75, 0.77, 0.79, 0.81, 0.83, 0.85],
                "loss": [1.2, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75],
                "round_time": [12.5, 13.2, 11.8, 12.1, 12.7, 13.0, 12.3, 11.9, 12.4, 12.6],
                "train_loss": [1.2, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75],
                "test_loss": [1.2, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75]
            },
            "client_ids": [f"client-{j}" for j in range(1, 9)]
        })
    return jobs


def generate_mock_clients() -> List[Dict[str, Any]]:
    """Generate mock client data"""
    clients = []
    for i in range(1, 11):
        status = "online" if i % 3 != 0 else "offline"
        clients.append({
            "id": f"client-{i}",
            "name": f"边缘设备 #{i}",
            "status": status,
            "device_type": "Edge Server",
            "connected_at": datetime.now() - timedelta(hours=i),
            "last_heartbeat": datetime.now() - timedelta(minutes=i*5) if status == "online" else None,
            "gpu": "NVIDIA RTX A6000" if i % 2 == 0 else "NVIDIA RTX 3080",
            "cpu": "Intel Core i7-8700K" if i % 2 == 0 else "Intel Core i9-10900K",
            "memory": "32 GB" if i % 2 == 0 else "64 GB",
            "os": "Ubuntu 20.04 LTS",
            "ip_address": f"192.168.1.{100+i}",
            "port": 50051 + i,
            "device_info": {
                "type": "Edge Server",
                "ipAddress": f"192.168.1.{100+i}",
                "port": 50051 + i,
                "os": "Ubuntu 20.04 LTS",
                "cpu": "Intel Core i7-8700K" if i % 2 == 0 else "Intel Core i9-10900K",
                "memory": "32 GB" if i % 2 == 0 else "64 GB",
                "gpu": "NVIDIA RTX A6000" if i % 2 == 0 else "NVIDIA RTX 3080"
            },
            "resource_usage": {
                "cpuUsage": 45.5 + (i * 2),
                "memoryUsage": 62.3 + (i * 1.5),
                "diskUsage": 30.1 + (i * 0.8),
                "networkIO": 125.6 + (i * 3)
            },
            "job_count": i,
            "participated_jobs": [
                {
                    "jobId": f"FL-2023-{j:03d}",
                    "jobName": f"医学图像分割任务 {j}",
                    "status": "completed",
                    "accuracy": 0.75 + (j * 0.02),
                    "completedAt": datetime.now() - timedelta(days=j)
                }
                for j in range(1, min(i+1, 6))
            ],
            "performance_metrics": {
                "days": i * 5,
                "trainingTime": 120.5 + (i * 10),
                "dataTransfer": 15.3 + (i * 2)
            }
        })
    return clients


def generate_mock_models() -> List[Dict[str, Any]]:
    """Generate mock model data"""
    models = []
    for i in range(1, 6):
        models.append({
            "id": f"model-{i}",
            "name": f"ResNet-50 联邦学习模型 {i}",
            "job_id": f"FL-2023-{i:03d}",
            "accuracy": 0.85 + (i * 0.02),
            "loss": 0.28 - (i * 0.02),
            "created_at": datetime.now() - timedelta(days=i),
            "createdAt": datetime.now() - timedelta(days=i),
            "framework": "PyTorch",
            "parameters": "25.6M",
            "size": "98.2 MB",
            "architecture": "ResNet-50",
            "dataset": "Medical Images",
            "rounds": 10,
            "clients": 8,
            "metrics": {
                "accuracy": [72, 78, 82, 85, 87, 89, 90, 91, 91.8, 92.4],
                "loss": [0.85, 0.72, 0.63, 0.55, 0.48, 0.42, 0.38, 0.34, 0.30, 0.28],
                "precision": [0.78, 0.82, 0.85, 0.87, 0.89, 0.91, 0.92, 0.93, 0.94, 0.95],
                "recall": [0.75, 0.79, 0.83, 0.86, 0.88, 0.90, 0.91, 0.92, 0.93, 0.94]
            }
        })
    return models


def generate_mock_data_quality() -> Dict[str, Any]:
    """Generate mock data quality data"""
    return {
        "stats": {
            "totalSamples": 125000,
            "missingRate": 3.2,
            "imbalanceScore": 0.15,
            "noiseLevel": 2.1,
            "criticalWarnings": 2,
            "warnings": 8,
            "infoAlerts": 15
        },
        "distribution": {
            "highQuality": 7,
            "mediumQuality": 2,
            "lowQuality": 1
        },
        "nodes": [
            {
                "nodeId": f"FL-{100+i}",
                "name": f"节点 #FL-{100+i}",
                "quality": 0.85 + (i * 0.02),
                "samples": 12500,
                "missingRate": 2.5 + (i * 0.3),
                "noiseLevel": 1.8 + (i * 0.2),
                "x": i * 2,
                "y": i * 1.5,
                "z": (0.85 + i * 0.02) * 5,
                "category": "high" if i <= 7 else ("medium" if i <= 9 else "low")
            }
            for i in range(1, 11)
        ],
        "warnings": [
            {
                "id": f"warn-{i}",
                "type": "critical" if i <= 2 else ("warning" if i <= 5 else "info"),
                "nodeId": f"FL-{100+i}",
                "title": f"节点 #FL-{100+i} 数据问题",
                "message": f"节点数据存在{i}个问题，需要检查。",
                "timestamp": f"{i}分钟前"
            }
            for i in range(1, 11)
        ]
    }


def generate_mock_settings() -> Dict[str, Any]:
    """Generate mock settings data"""
    return {
        "connection": {
            "adminApiEndpoint": "http://localhost:8200",
            "port": 8200,
            "protocol": "http",
            "certificate": None
        },
        "workspace": {
            "secureWorkspacePath": "/opt/fedlbe/secure_workspace",
            "pocWorkspacePath": "/opt/fedlbe/poc_workspace",
            "deploymentMode": "poc"
        },
        "security": {
            "enableSecureComm": True,
            "enableSecureAgg": True,
            "enableDiffPrivacy": False,
            "noiseLevel": 0.5,
            "clippingNorm": 1.0
        },
        "users": [
            {
                "id": "user-1",
                "username": "admin",
                "role": "admin",
                "status": "active",
                "email": "admin@example.com",
                "fullName": "管理员"
            },
            {
                "id": "user-2",
                "username": "researcher",
                "role": "researcher",
                "status": "active",
                "email": "researcher@example.com",
                "fullName": "研究员"
            }
        ]
    }


def job_to_response(job: Dict[str, Any]) -> Dict[str, Any]:
    """Convert mock job data to response format"""
    clients = []
    for client_id in job["client_ids"]:
        client = next((c for c in mock_clients if c["id"] == client_id), None)
        if client:
            clients.append(JobClient(
                id=client["id"],
                name=client["name"],
                status=client["status"],
                gpu=client["gpu"]
            ))

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
        "config": job["config"],
        "clients": clients,
        "metrics": JobMetrics(**job["metrics"])
    }


# Global mock data
mock_jobs = generate_mock_jobs()
mock_clients = generate_mock_clients()
mock_models = generate_mock_models()
mock_data_quality = generate_mock_data_quality()
mock_settings = generate_mock_settings()
