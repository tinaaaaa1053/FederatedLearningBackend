"""
Data Quality API routes
"""
from fastapi import APIRouter, Depends
from typing import List

from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.data_quality import (
    QualityStats, QualityDistribution, NodeQuality,
    Warning, WarningListRequest
)
from app.services import DataQualityService, MockDataQualityService

router = APIRouter()


@router.get("/stats", response_model=ApiResponse[QualityStats])
async def get_quality_stats(
    service: DataQualityService = Depends()
):
    """获取数据质量统计"""
    stats = await service.get_quality_stats()
    return ApiResponse(data=stats)


@router.get("/nodes", response_model=ApiResponse[List[NodeQuality]])
async def get_node_quality_data(
    service: DataQualityService = Depends()
):
    """获取节点质量数据（用于3D可视化）"""
    nodes = await service.get_node_quality_data()
    return ApiResponse(data=nodes)


@router.get("/distribution", response_model=ApiResponse[QualityDistribution])
async def get_quality_distribution(
    service: DataQualityService = Depends()
):
    """获取数据质量分布"""
    distribution = await service.get_quality_distribution()
    return ApiResponse(data=distribution)


@router.post("/warnings", response_model=ApiResponse[PaginatedResponse[Warning]])
async def get_warnings(
    params: WarningListRequest,
    service: DataQualityService = Depends()
):
    """获取警告列表（分页）"""
    result = await service.get_warnings(
        page=params.pageNo,
        page_size=params.pageSize,
        warning_type=params.type
    )
    return ApiResponse(data=result)


@router.post("/report")
async def generate_quality_report(
    service: DataQualityService = Depends()
):
    """生成数据质量报告（PDF）"""
    from fastapi.responses import StreamingResponse
    from io import BytesIO

    report_data = await service.generate_report()
    if not report_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Failed to generate report")

    buffer = BytesIO(report_data)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=data_quality_report.pdf"
        }
    )
