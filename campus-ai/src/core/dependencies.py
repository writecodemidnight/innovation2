"""依赖注入模块"""

import uuid
from typing import Annotated, Optional, TYPE_CHECKING
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from .config import get_settings, Settings

# 条件导入，避免循环依赖
if TYPE_CHECKING:
    from ..services.model_manager import ModelManager
    from ..utils.spring_client import SpringBootClient

# 模块级单例缓存
_model_manager_instance: Optional["ModelManager"] = None
_spring_client_instance: Optional["SpringBootClient"] = None

# ============ 认证依赖 ============
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings)
) -> Optional[dict]:
    """获取当前用户信息（从Spring Boot验证JWT）"""
    if not credentials:
        # 开发环境允许匿名访问
        if settings.debug:
            logger.debug("开发模式：允许匿名访问")
            return {"user_id": "anonymous", "role": "guest"}
        return None

    try:
        # 这里应该调用Spring Boot验证JWT
        # 简化实现：直接解析token或调用验证接口
        token = credentials.credentials
        logger.debug(f"验证Token: {token[:20]}...")

        # 在实际实现中，这里应该调用Spring Boot验证token
        # 暂时返回模拟用户
        return {"user_id": "user_001", "role": "student", "club_id": "club_001"}

    except Exception as e:
        logger.error(f"Token验证失败: {e}")
        return None

def require_auth(
    user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """要求认证的依赖"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def require_admin(
    user: dict = Depends(require_auth)
) -> dict:
    """要求管理员权限的依赖"""
    if user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user

# ============ 服务依赖（单例模式） ============
def _get_model_manager_instance() -> Optional["ModelManager"]:
    """获取或创建模型管理器单例"""
    global _model_manager_instance
    if _model_manager_instance is None:
        try:
            from ..services.model_manager import ModelManager
            from ..utils.oss_client import OSSClient
            settings = get_settings()
            oss_client = OSSClient(settings)
            _model_manager_instance = ModelManager(oss_client, settings)
            logger.info("ModelManager 单例初始化完成")
        except ImportError:
            logger.warning("ModelManager未实现，返回None")
            return None
    return _model_manager_instance

def _get_spring_client_instance() -> Optional["SpringBootClient"]:
    """获取或创建Spring Boot客户端单例"""
    global _spring_client_instance
    if _spring_client_instance is None:
        try:
            from ..utils.spring_client import SpringBootClient
            settings = get_settings()
            _spring_client_instance = SpringBootClient(
                settings.spring_api_base_url, settings.spring_auth_token
            )
            logger.info("SpringBootClient 单例初始化完成")
        except ImportError:
            logger.warning("SpringBootClient未实现，返回None")
            return None
    return _spring_client_instance

async def get_model_manager() -> Optional["ModelManager"]:
    """获取模型管理器依赖（单例）"""
    return _get_model_manager_instance()

async def get_spring_client() -> Optional["SpringBootClient"]:
    """获取Spring Boot客户端依赖（单例）"""
    return _get_spring_client_instance()

# ============ 通用依赖 ============
def get_pagination_params(
    skip: int = 0,
    limit: int = 10
) -> dict:
    """分页参数依赖"""
    return {"skip": max(0, skip), "limit": min(100, max(1, limit))}

def get_request_id(
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> str:
    """获取请求ID依赖"""
    return x_request_id or str(uuid.uuid4())

# 类型别名，便于在路由中使用
SettingsDep = Annotated[Settings, Depends(get_settings)]
CurrentUserDep = Annotated[Optional[dict], Depends(get_current_user)]
RequireAuthDep = Annotated[dict, Depends(require_auth)]
RequireAdminDep = Annotated[dict, Depends(require_admin)]
ModelManagerDep = Annotated[Optional["ModelManager"], Depends(get_model_manager)]
SpringClientDep = Annotated[Optional["SpringBootClient"], Depends(get_spring_client)]
PaginationDep = Annotated[dict, Depends(get_pagination_params)]
RequestIdDep = Annotated[str, Depends(get_request_id)]