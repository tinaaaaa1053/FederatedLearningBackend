"""
Job Management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
from io import BytesIO

from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.job import (
    JobCreate, JobResponse, JobListRequest,
    JobDetailResponse, JobMetricsResponse
)
from app.services import JobService, MockJobService

router = APIRouter()


@router.post("/list", response_model=ApiResponse[PaginatedResponse[JobResponse]])
async def get_job_list(
    params: JobListRequest,
    service: JobService = Depends()
):
    """获取任务列表（分页）"""
    result = await service.get_job_list(
        page=params.pageNo,
        page_size=params.pageSize,
        status=params.status,
        keyword=params.keyword
    )
    return ApiResponse(data=result)


@router.get("/detail/{job_id}", response_model=ApiResponse[JobDetailResponse])
async def get_job_detail(
    job_id: str,
    service: JobService = Depends()
):
    """获取任务详情"""
    job = await service.get_job_detail(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ApiResponse(data=job)


@router.post("/create", response_model=ApiResponse[dict])
async def create_job(
    job_data: JobCreate,
    service: JobService = Depends()
):
    """创建新任务"""
    job = await service.create_job(job_data)
    return ApiResponse(data={"jobId": job.id, "status": job.status})


@router.post("/abort/{job_id}", response_model=ApiResponse[dict])
async def abort_job(
    job_id: str,
    service: JobService = Depends()
):
    """中止任务"""
    job = await service.abort_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ApiResponse(data={"jobId": job.id, "status": job.status})


@router.get("/logs/{job_id}")
async def download_job_logs(
    job_id: str,
    service: JobService = Depends()
):
    """下载任务日志文件"""
    logs = await service.get_job_logs(job_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Job logs not found")

    # Return as downloadable file
    buffer = BytesIO(logs.encode('utf-8'))
    return StreamingResponse(
        buffer,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=job_{job_id}_logs.txt"
        }
    )


@router.get("/metrics/{job_id}", response_model=ApiResponse[JobMetricsResponse])
async def get_job_metrics(
    job_id: str,
    service: JobService = Depends()
):
    """获取任务指标数据"""
    metrics = await service.get_job_metrics(job_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Job metrics not found")
    return ApiResponse(data=metrics)


@router.post("/upload-model/{job_id}", response_model=ApiResponse[dict])
async def upload_model_file(
    job_id: str,
    file: UploadFile = File(...),
    service: JobService = Depends()
):
    """上传模型文件（用于任务创建时）"""
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python files are allowed")

    content = await file.read()
    result = await service.save_model_file(job_id, file.filename, content)
    return ApiResponse(data=result)
