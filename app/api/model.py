"""
Model Management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
from io import BytesIO

from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.model import (
    ModelResponse, ModelDetailResponse, ModelListRequest,
    ModelUpload, ModelComparisonRequest, ModelComparison
)
from app.services import ModelService, MockModelService

router = APIRouter()


@router.post("/list", response_model=ApiResponse[PaginatedResponse[ModelResponse]])
async def get_model_list(
    params: ModelListRequest,
    service: ModelService = Depends()
):
    """获取模型列表（分页）"""
    result = await service.get_model_list(
        page=params.pageNo,
        page_size=params.pageSize,
        keyword=params.keyword,
        job_id=params.jobId
    )
    return ApiResponse(data=result)


@router.get("/detail/{model_id}", response_model=ApiResponse[ModelDetailResponse])
async def get_model_detail(
    model_id: str,
    service: ModelService = Depends()
):
    """获取模型详情"""
    model = await service.get_model_detail(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return ApiResponse(data=model)


@router.post("/upload", response_model=ApiResponse[dict])
async def upload_model(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    job_id: Optional[str] = None,
    framework: Optional[str] = "PyTorch",
    architecture: Optional[str] = None,
    service: ModelService = Depends()
):
    """上传模型文件"""
    content = await file.read()
    model = await service.upload_model(
        name=name or file.filename,
        file_content=content,
        file_name=file.filename,
        job_id=job_id,
        framework=framework,
        architecture=architecture
    )
    return ApiResponse(data={"modelId": model.id, "status": "uploaded"})


@router.get("/download/{model_id}")
async def download_model(
    model_id: str,
    service: ModelService = Depends()
):
    """下载模型文件"""
    model_data = await service.get_model_file(model_id)
    if not model_data:
        raise HTTPException(status_code=404, detail="Model file not found")

    file_content, file_name = model_data
    buffer = BytesIO(file_content)
    return StreamingResponse(
        buffer,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    )


@router.post("/validate/{model_id}", response_model=ApiResponse[dict])
async def validate_model(
    model_id: str,
    service: ModelService = Depends()
):
    """验证模型"""
    result = await service.validate_model(model_id)
    return ApiResponse(data=result)


@router.post("/comparison", response_model=ApiResponse[ModelComparison])
async def compare_models(
    request: ModelComparisonRequest,
    service: ModelService = Depends()
):
    """对比模型（最多2个）"""
    comparison = await service.compare_models(request.modelIds)
    return ApiResponse(data=comparison)


@router.post("/delete/{model_id}", response_model=ApiResponse[dict])
async def delete_model(
    model_id: str,
    service: ModelService = Depends()
):
    """删除模型"""
    result = await service.delete_model(model_id)
    if not result:
        raise HTTPException(status_code=404, detail="Model not found")
    return ApiResponse(data={"message": "Model deleted successfully"})
