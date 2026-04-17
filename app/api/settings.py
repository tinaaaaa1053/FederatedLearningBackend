"""
Settings API routes
"""
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.common import ApiResponse
from app.schemas.settings import (
    SettingsResponse, SettingsSave, TestConnectionRequest,
    TestConnectionResponse, UserCreate, UserUpdate, UserInfo
)
from app.services import SettingsService, MockSettingsService

router = APIRouter()


@router.get("/get", response_model=ApiResponse[SettingsResponse])
async def get_settings(
    service: SettingsService = Depends()
):
    """获取所有设置"""
    settings = await service.get_settings()
    return ApiResponse(data=settings)


@router.post("/save", response_model=ApiResponse[dict])
async def save_settings(
    settings_data: SettingsSave,
    service: SettingsService = Depends()
):
    """保存设置"""
    await service.save_settings(settings_data)
    return ApiResponse(data={"message": "Settings saved successfully"})


@router.post("/testConnection", response_model=ApiResponse[TestConnectionResponse])
async def test_connection(
    request: TestConnectionRequest,
    service: SettingsService = Depends()
):
    """测试后端连接"""
    result = await service.test_connection(request)
    return ApiResponse(data=result)


@router.post("/user/add", response_model=ApiResponse[dict])
async def add_user(
    user_data: UserCreate,
    service: SettingsService = Depends()
):
    """添加用户"""
    # --- 修改后 ---
    user = await service.create_user(user_data)
    # 注意：这里改用方括号 [] 来访问字典里的值
    return ApiResponse(data={"userId": user["id"], "username": user["username"]})


@router.post("/user/update/{user_id}", response_model=ApiResponse[dict])
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: SettingsService = Depends()
):
    """更新用户"""
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(data={"message": "User updated successfully"})


@router.post("/user/delete/{user_id}", response_model=ApiResponse[dict])
async def delete_user(
    user_id: str,
    service: SettingsService = Depends()
):
    """删除用户"""
    result = await service.delete_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return ApiResponse(data={"message": "User deleted successfully"})


@router.post("/reset", response_model=ApiResponse[dict])
async def reset_settings(
    service: SettingsService = Depends()
):
    """重置为默认设置"""
    await service.reset_settings()
    return ApiResponse(data={"message": "Settings reset to defaults"})
