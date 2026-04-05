"""
Mock data for testing
"""
from datetime import datetime
from app.schemas.data_quality import QualityStats, QualityDistribution, NodeQuality, Warning
from app.schemas.settings import SettingsResponse, ConnectionSettings, WorkspaceSettings, SecuritySettings
from typing import List

# Mock jobs data
mock_jobs = [
    {
        "id": "job-001",
        "name": "肺炎X光影像分类训练",
        "description": "使用FedAvg算法进行肺炎X光影像分类模型训练",
        "status": "running",
        "job_type": "classification",
        "algorithm": "FedAvg算法",
        "current_round": 5,
        "total_rounds": 20,
        "accuracy": 0.85,
        "loss": 0.32,
        "created_at": datetime.now(),
        "started_at": datetime.now(),
        "completed_at": None,
        "config": {"learning_rate": 0.001, "batch_size": 32},
        "metrics": {
            "accuracy": [0.65, 0.72, 0.78, 0.82, 0.85],
            "loss": [1.2, 0.95, 0.72, 0.52, 0.32],
            "precision": [0.70, 0.75, 0.80, 0.84, 0.87],
            "recall": [0.68, 0.73, 0.78, 0.82, 0.85],
            "f1Score": [0.69, 0.74, 0.79, 0.83, 0.86]
        },
        "client_ids": ["client-001", "client-002", "client-003"]
    },
    {
        "id": "job-002",
        "name": "皮肤病分类模型训练",
        "description": "多中心皮肤病数据集联邦学习",
        "status": "pending",
        "job_type": "classification",
        "algorithm": "FedProx算法",
        "current_round": 0,
        "total_rounds": 30,
        "accuracy": 0.0,
        "loss": 0.0,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "config": {"learning_rate": 0.0005, "batch_size": 64},
        "metrics": {"accuracy": [], "loss": []},
        "client_ids": ["client-001", "client-004", "client-005", "client-006"]
    },
    {
        "id": "job-003",
        "name": "脑肿瘤分割任务",
        "description": "基于联邦学习的脑肿瘤图像分割",
        "status": "completed",
        "job_type": "segmentation",
        "algorithm": "FedAvg算法",
        "current_round": 25,
        "total_rounds": 25,
        "accuracy": 0.92,
        "loss": 0.18,
        "created_at": datetime.now(),
        "started_at": datetime.now(),
        "completed_at": datetime.now(),
        "config": {"learning_rate": 0.001, "batch_size": 16},
        "metrics": {
            "accuracy": [0.55, 0.62, 0.68, 0.74, 0.79, 0.83, 0.86, 0.88, 0.90, 0.92],
            "loss": [1.5, 1.2, 0.95, 0.75, 0.58, 0.45, 0.35, 0.28, 0.22, 0.18]
        },
        "client_ids": ["client-002", "client-003", "client-007", "client-008"]
    }
]

# Mock clients data
mock_clients = [
    {
        "id": "client-001",
        "name": "北京协和医院-影像科",
        "status": "online",
        "device_type": "gpu",
        "ip_address": "192.168.1.101",
        "port": 8300,
        "fedlbe_port": 8200,
        "gpu": "NVIDIA A100 40GB",
        "cpu": "Intel Xeon Gold 6248",
        "memory": "256GB",
        "os": "Ubuntu 20.04",
        "connected_at": datetime.now(),
        "last_heartbeat": datetime.now(),
        "job_count": 3,
        "device_info": {
            "type": "gpu",
            "ipAddress": "192.168.1.101",
            "port": 8300,
            "os": "Ubuntu 20.04",
            "cpu": "Intel Xeon Gold 6248",
            "memory": "256GB",
            "gpu": "NVIDIA A100 40GB"
        },
        "resource_usage": {
            "cpuUsage": 45.2,
            "memoryUsage": 38.7,
            "diskUsage": 62.3,
            "networkIO": 125.6
        },
        "participated_jobs": ["job-001", "job-003"],
        "performance_metrics": {
            "days": 15,
            "trainingTime": 48.5,
            "dataTransfer": 1024.0
        }
    },
    {
        "id": "client-002",
        "name": "上海瑞金医院-放射科",
        "status": "online",
        "device_type": "gpu",
        "ip_address": "192.168.1.102",
        "port": 8300,
        "fedlbe_port": 8200,
        "gpu": "NVIDIA V100 32GB",
        "cpu": "Intel Xeon Gold 5218",
        "memory": "128GB",
        "os": "Ubuntu 20.04",
        "connected_at": datetime.now(),
        "last_heartbeat": datetime.now(),
        "job_count": 2,
        "device_info": {
            "type": "gpu",
            "ipAddress": "192.168.1.102",
            "port": 8300,
            "os": "Ubuntu 20.04",
            "cpu": "Intel Xeon Gold 5218",
            "memory": "128GB",
            "gpu": "NVIDIA V100 32GB"
        },
        "resource_usage": {
            "cpuUsage": 52.8,
            "memoryUsage": 45.3,
            "diskUsage": 58.7,
            "networkIO": 98.4
        },
        "participated_jobs": ["job-001", "job-003"],
        "performance_metrics": {
            "days": 12,
            "trainingTime": 42.3,
            "dataTransfer": 896.0
        }
    },
    {
        "id": "client-003",
        "name": "广州中山医院-病理科",
        "status": "online",
        "device_type": "cpu",
        "ip_address": "192.168.1.103",
        "port": 8300,
        "fedlbe_port": 8200,
        "gpu": None,
        "cpu": "Intel Xeon Gold 6240",
        "memory": "64GB",
        "os": "Ubuntu 20.04",
        "connected_at": datetime.now(),
        "last_heartbeat": datetime.now(),
        "job_count": 2,
        "device_info": {
            "type": "cpu",
            "ipAddress": "192.168.1.103",
            "port": 8300,
            "os": "Ubuntu 20.04",
            "cpu": "Intel Xeon Gold 6240",
            "memory": "64GB",
            "gpu": None
        },
        "resource_usage": {
            "cpuUsage": 78.3,
            "memoryUsage": 62.1,
            "diskUsage": 45.8,
            "networkIO": 156.2
        },
        "participated_jobs": ["job-001", "job-003"],
        "performance_metrics": {
            "days": 10,
            "trainingTime": 35.8,
            "dataTransfer": 768.0
        }
    },
    {
        "id": "client-004",
        "name": "武汉同济医院-影像科",
        "status": "offline",
        "device_type": "gpu",
        "ip_address": "192.168.1.104",
        "port": 8300,
        "fedlbe_port": 8200,
        "gpu": "NVIDIA RTX 3090 24GB",
        "cpu": "AMD EPYC 7302",
        "memory": "128GB",
        "os": "Ubuntu 20.04",
        "connected_at": None,
        "last_heartbeat": datetime.now(),
        "job_count": 1,
        "device_info": {
            "type": "gpu",
            "ipAddress": "192.168.1.104",
            "port": 8300,
            "os": "Ubuntu 20.04",
            "cpu": "AMD EPYC 7302",
            "memory": "128GB",
            "gpu": "NVIDIA RTX 3090 24GB"
        },
        "resource_usage": {
            "cpuUsage": 0,
            "memoryUsage": 0,
            "diskUsage": 0,
            "networkIO": 0
        },
        "participated_jobs": ["job-002"],
        "performance_metrics": {
            "days": 5,
            "trainingTime": 18.2,
            "dataTransfer": 384.0
        }
    },
    {
        "id": "client-005",
        "name": "成都华西医院-放射科",
        "status": "offline",
        "device_type": "gpu",
        "ip_address": "192.168.1.105",
        "port": 8300,
        "fedlbe_port": 8200,
        "gpu": "NVIDIA A10 24GB",
        "cpu": "Intel Xeon Silver 4214",
        "memory": "96GB",
        "os": "Ubuntu 20.04",
        "connected_at": None,
        "last_heartbeat": datetime.now(),
        "job_count": 0,
        "device_info": {
            "type": "gpu",
            "ipAddress": "192.168.1.105",
            "port": 8300,
            "os": "Ubuntu 20.04",
            "cpu": "Intel Xeon Silver 4214",
            "memory": "96GB",
            "gpu": "NVIDIA A10 24GB"
        },
        "resource_usage": {
            "cpuUsage": 0,
            "memoryUsage": 0,
            "diskUsage": 0,
            "networkIO": 0
        },
        "participated_jobs": [],
        "performance_metrics": {
            "days": 0,
            "trainingTime": 0,
            "dataTransfer": 0
        }
    }
]

# Mock models data
mock_models = [
    {
        "id": "model-001",
        "name": "肺炎检测模型v1",
        "job_id": "job-001",
        "accuracy": 0.852,
        "loss": 0.321,
        "createdAt": datetime.now(),
        "framework": "PyTorch",
        "parameters": "25.6M",
        "size": "98.2 MB",
        "architecture": "ResNet-50",
        "dataset": "ChestX-ray2017",
        "rounds": 20,
        "clients": 3,
        "metrics": {
            "accuracy": [65, 72, 78, 82, 85.2],
            "loss": [1.2, 0.95, 0.72, 0.52, 0.321],
            "precision": [70, 75, 80, 84, 87],
            "recall": [68, 73, 78, 82, 85]
        }
    },
    {
        "id": "model-002",
        "name": "皮肤病变分类模型",
        "job_id": "job-002",
        "accuracy": 0.784,
        "loss": 0.452,
        "createdAt": datetime.now(),
        "framework": "TensorFlow",
        "parameters": "18.2M",
        "size": "72.5 MB",
        "architecture": "EfficientNet-B3",
        "dataset": "ISIC 2020",
        "rounds": 15,
        "clients": 4,
        "metrics": {
            "accuracy": [58, 65, 71, 75, 78.4],
            "loss": [1.4, 1.1, 0.85, 0.62, 0.452],
            "precision": [62, 68, 74, 78, 81],
            "recall": [60, 66, 72, 76, 79]
        }
    }
]

# Mock data quality data
mock_data_quality = {
    "stats": QualityStats(
        totalSamples=125000,
        missingRate=3.2,
        imbalanceScore=0.15,
        noiseLevel=2.1,
        criticalWarnings=2,
        warnings=8,
        infoAlerts=15
    ),
    "nodes": [
        NodeQuality(
            nodeId="FL-101",
            name="节点 #FL-101",
            quality=0.85,
            samples=15234,
            missingRate=2.3,
            noiseLevel=1.8,
            x=-2.5,
            y=1.2,
            z=4.25,
            category="high"
        ),
        NodeQuality(
            nodeId="FL-205",
            name="节点 #FL-205",
            quality=0.62,
            samples=8234,
            missingRate=8.5,
            noiseLevel=4.2,
            x=1.8,
            y=-1.5,
            z=3.1,
            category="medium"
        ),
        NodeQuality(
            nodeId="FL-302",
            name="节点 #FL-302",
            quality=0.45,
            samples=5234,
            missingRate=15.2,
            noiseLevel=6.8,
            x=3.2,
            y=2.5,
            z=2.25,
            category="low"
        ),
        NodeQuality(
            nodeId="FL-418",
            name="节点 #FL-418",
            quality=0.78,
            samples=12500,
            missingRate=4.5,
            noiseLevel=2.8,
            x=-1.2,
            y=-2.8,
            z=3.9,
            category="high"
        ),
        NodeQuality(
            nodeId="FL-505",
            name="节点 #FL-505",
            quality=0.55,
            samples=6800,
            missingRate=10.2,
            noiseLevel=5.1,
            x=0.5,
            y=3.5,
            z=2.75,
            category="medium"
        )
    ],
    "distribution": QualityDistribution(
        highQuality=3,
        mediumQuality=2,
        lowQuality=1
    ),
    "warnings": [
        {
            "id": "warn-001",
            "type": "critical",
            "nodeId": "FL-842",
            "title": "节点 #FL-842 严重数据缺失",
            "message": "节点数据缺失率超过阈值，当前缺失率为 12.5%，建议检查数据源或暂停该节点参与训练。",
            "timestamp": "10分钟前"
        },
        {
            "id": "warn-002",
            "type": "warning",
            "nodeId": "FL-205",
            "title": "节点 #FL-205 数据不平衡",
            "message": "节点数据类别分布不均，最大类别占比 78%，可能影响模型训练效果。",
            "timestamp": "25分钟前"
        },
        {
            "id": "warn-003",
            "type": "info",
            "nodeId": "FL-302",
            "title": "节点 #FL-302 数据量偏低",
            "message": "节点数据量低于平均值，建议增加数据采集或调整采样权重。",
            "timestamp": "1小时前"
        }
    ]
}

# Mock settings data
mock_settings = SettingsResponse(
    connection=ConnectionSettings(
        adminApiEndpoint="http://localhost:8200",
        port=8200,
        protocol="http",
        certificate=None
    ),
    workspace=WorkspaceSettings(
        secureWorkspacePath="/opt/fedlbe/secure_workspace",
        pocWorkspacePath="/opt/fedlbe/poc_workspace",
        deploymentMode="poc"
    ),
    security=SecuritySettings(
        enableSecureComm=True,
        enableSecureAgg=True,
        enableDiffPrivacy=False,
        noiseLevel=0.5,
        clippingNorm=1.0
    ),
    users=[
        {
            "id": "user-001",
            "username": "admin",
            "role": "admin",
            "status": "active",
            "email": "admin@example.com",
            "fullName": "Administrator"
        },
        {
            "id": "user-002",
            "username": "researcher",
            "role": "researcher",
            "status": "active",
            "email": "researcher@example.com",
            "fullName": "Researcher"
        }
    ]
)