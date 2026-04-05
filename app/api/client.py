"""
Client Management API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.client import (
    ClientResponse, ClientDetailResponse, ClientListRequest,
    ClientCreate, ClientUpdate
)
from app.services import ClientService, MockClientService

router = APIRouter()


@router.post("/list", response_model=ApiResponse[PaginatedResponse[ClientResponse]])
async def get_client_list(
    params: ClientListRequest,
    service: ClientService = Depends()
):
    """获取客户端列表（分页）"""
    result = await service.get_client_list(
        page=params.pageNo,
        page_size=params.pageSize,
        status=params.status,
        keyword=params.keyword
    )
    return ApiResponse(data=result)


@router.get("/detail/{client_id}", response_model=ApiResponse[ClientDetailResponse])
async def get_client_detail(
    client_id: str,
    service: ClientService = Depends()
):
    """获取客户端详情"""
    client = await service.get_client_detail(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ApiResponse(data=client)


@router.post("/add", response_model=ApiResponse[dict])
async def add_client(
    client_data: ClientCreate,
    service: ClientService = Depends()
):
    """添加新客户端"""
    client = await service.create_client(client_data)
    return ApiResponse(data={"clientId": client.id, "status": client.status})


@router.post("/delete/{client_id}", response_model=ApiResponse[dict])
async def delete_client(
    client_id: str,
    service: ClientService = Depends()
):
    """删除客户端"""
    result = await service.delete_client(client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return ApiResponse(data={"message": "Client deleted successfully"})


@router.post("/update/{client_id}", response_model=ApiResponse[dict])
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    service: ClientService = Depends()
):
    """更新客户端信息"""
    client = await service.update_client(client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ApiResponse(data={"clientId": client.id, "status": "updated"})


@router.post("/reconnect/{client_id}", response_model=ApiResponse[dict])
async def reconnect_client(
    client_id: str,
    service: ClientService = Depends()
):
    """重新连接客户端"""
    result = await service.reconnect_client(client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return ApiResponse(data={"clientId": client_id, "status": "reconnecting"})


@router.get("/online", response_model=ApiResponse[list])
async def get_online_clients(
    service: ClientService = Depends()
):
    """获取在线客户端列表"""
    clients = await service.get_online_clients()
    return ApiResponse(data=clients)
