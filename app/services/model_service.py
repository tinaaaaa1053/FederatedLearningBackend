"""
Model Management Service
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import SessionLocal
from app.models.model import Model
from app.models.job import Job, JobStatus
from app.schemas.model import (
    ModelResponse, ModelDetailResponse, ModelUpload, ModelComparison
)
from app.schemas.common import PaginatedResponse
from app.fedlbe.storage_client import StorageServiceClient


class ModelService:
    """Service for model management operations"""

    def __init__(self):
        self.db: Session = SessionLocal()
        self.storage_client = StorageServiceClient()

    def _model_to_response(self, model: Model) -> ModelResponse:
        """Convert Model to ModelResponse schema"""
        return ModelResponse(
            id=model.id,
            name=model.name,
            jobId=model.job_id,
            accuracy=model.accuracy or 0.0,
            loss=model.loss or 0.0,
            createdAt=model.created_at,
            framework=model.framework,
            parameters=model.parameters,
            size=model.size,
            architecture=model.architecture,
            dataset=model.dataset,
            rounds=model.rounds,
            clients=model.clients,
            metrics=model.metrics
        )

    async def get_model_list(
        self, page: int = 1, page_size: int = 10,
        keyword: Optional[str] = None, job_id: Optional[str] = None
    ) -> PaginatedResponse[ModelResponse]:
        """Get paginated model list"""
        query = self.db.query(Model)

        if keyword:
            query = query.filter(
                or_(
                    Model.name.ilike(f"%{keyword}%"),
                    Model.id.ilike(f"%{keyword}%")
                )
            )

        if job_id:
            query = query.filter(Model.job_id == job_id)

        total = query.count()
        models = query.order_by(Model.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return PaginatedResponse(
            records=[self._model_to_response(m) for m in models],
            total=total,
            pageNo=page,
            pageSize=page_size
        )

    async def get_model_detail(self, model_id: str) -> Optional[ModelDetailResponse]:
        """Get model detail by ID"""
        model = self.db.query(Model).filter(Model.id == model_id).first()
        if not model:
            return None

        return ModelDetailResponse(
            id=model.id,
            name=model.name,
            jobId=model.job_id,
            accuracy=model.accuracy or 0.0,
            loss=model.loss or 0.0,
            createdAt=model.created_at,
            framework=model.framework,
            parameters=model.parameters,
            size=model.size,
            architecture=model.architecture,
            dataset=model.dataset,
            rounds=model.rounds,
            clients=model.clients,
            metrics=model.metrics
        )

    async def upload_model(
        self, name: str, file_content: bytes, file_name: str,
        job_id: Optional[str] = None, framework: str = "PyTorch",
        architecture: Optional[str] = None
    ) -> Model:
        """Upload a model file"""
        import os

        # Create models directory
        models_dir = os.path.join(os.getcwd(), "saved_models")
        os.makedirs(models_dir, exist_ok=True)

        # Save file
        model = Model(
            name=name,
            job_id=job_id,
            framework=framework,
            architecture=architecture,
            size=f"{len(file_content) / (1024 * 1024):.1f} MB"
        )

        file_path = os.path.join(models_dir, f"{model.id}_{file_name}")
        with open(file_path, "wb") as f:
            f.write(file_content)

        model.file_path = file_path

        # If from a job, get job metrics
        if job_id:
            job = self.db.query(Job).filter(Job.id == job_id).first()
            if job:
                model.accuracy = job.accuracy
                model.loss = job.loss
                model.rounds = job.total_rounds
                model.clients = len(job.client_ids or [])
                model.metrics = job.metrics

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    async def get_model_file(self, model_id: str) -> Optional[Tuple[bytes, str]]:
        """Get model file for download"""
        model = self.db.query(Model).filter(Model.id == model_id).first()
        if not model or not model.file_path:
            return None

        try:
            with open(model.file_path, "rb") as f:
                content = f.read()

            file_name = model.file_path.split("/")[-1]
            # Remove model_id prefix from filename
            if file_name.startswith(model_id + "_"):
                file_name = file_name[len(model_id) + 1:]

            return content, file_name
        except FileNotFoundError:
            return None

    async def validate_model(self, model_id: str) -> dict:
        """Validate model architecture"""
        model = self.db.query(Model).filter(Model.id == model_id).first()
        if not model:
            return {"valid": False, "error": "Model not found"}

        # TODO: Implement actual model validation
        # - Check if model file exists
        # - Try to load model in PyTorch/TensorFlow
        # - Check if model can process test input

        return {
            "valid": True,
            "modelId": model_id,
            "framework": model.framework,
            "architecture": model.architecture
        }

    async def compare_models(self, model_ids: List[str]) -> ModelComparison:
        """Compare multiple models"""
        models = self.db.query(Model).filter(Model.id.in_(model_ids)).all()

        comparison_data = {}
        for model in models:
            comparison_data[model.id] = {
                "name": model.name,
                "accuracy": model.accuracy,
                "loss": model.loss,
                "rounds": model.rounds,
                "clients": model.clients,
                "framework": model.framework,
                "metrics": model.metrics
            }

        return ModelComparison(
            modelIds=model_ids,
            comparisonData=comparison_data
        )

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        model = self.db.query(Model).filter(Model.id == model_id).first()
        if not model:
            return False

        # Delete file if exists
        if model.file_path:
            import os
            try:
                os.remove(model.file_path)
            except FileNotFoundError:
                pass

        self.db.delete(model)
        self.db.commit()
        return True

    async def sync_from_storage_service(self, user_name: str) -> List[Model]:
        """Sync models from FedLBE StorageService"""
        tasks = await self.storage_client.get_tasks(user_name)

        models = []
        for task in tasks:
            # Check if model already exists
            existing = self.db.query(Model).filter(
                Model.job_id == task.get("task_name")
            ).first()

            if not existing:
                model = Model(
                    name=f"Model from {task.get('task_name')}",
                    job_id=task.get("task_name"),
                    created_at=task.get("date")
                )
                self.db.add(model)
                models.append(model)

        self.db.commit()
        return models
