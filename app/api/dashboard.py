"""
Dashboard API routes
"""
from fastapi import APIRouter, Depends
from typing import List
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardStats, ClientInfo, CurrentJob, ChartData
from app.services import JobService  # 这现在会从 __init__.py 获取 MockJobService

router = APIRouter()


@router.get("/stats", response_model=ApiResponse[DashboardStats])
async def get_dashboard_stats(
    service: JobService = Depends()
):
    """获取仪表盘统计数据"""
    stats = await service.get_dashboard_stats()
    return ApiResponse(data=stats)


@router.get("/clients", response_model=ApiResponse[List[ClientInfo]])
async def get_dashboard_clients(
    service: JobService = Depends()
):
    """获取已连接的客户端列表"""
    clients = await service.get_dashboard_clients()
    return ApiResponse(data=clients)


@router.get("/currentJob", response_model=ApiResponse[CurrentJob])
async def get_current_job(
    service: JobService = Depends()
):
    """获取当前运行中的任务进度"""
    job = await service.get_current_job()
    return ApiResponse(data=job)


@router.get("/logs", response_model=ApiResponse[List[str]])
async def get_realtime_logs(
    service: JobService = Depends()
):
    """获取实时日志"""
    logs = await service.get_realtime_logs()
    return ApiResponse(data=logs)


@router.get("/chart/{chart_type}", response_model=ApiResponse[ChartData])
async def get_chart_data(
    chart_type: str,
    service: JobService = Depends()
):
    """获取图表数据 (accuracy/loss)"""
    data = await service.get_chart_data(chart_type)
    return ApiResponse(data=data)
