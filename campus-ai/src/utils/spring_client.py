import httpx
from typing import Optional, Dict, Any
from loguru import logger
from ..core.config import get_settings

class SpringBootClient:
    """Spring Boot后端API客户端"""

    def __init__(self, base_url: str = None, auth_token: str = None):
        self.settings = get_settings()
        self.base_url = base_url or self.settings.spring_api_base_url
        self.auth_token = auth_token or self.settings.spring_auth_token
        self._client = None

    @property
    def client(self):
        """获取HTTP客户端（懒加载）"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.settings.spring_api_timeout,
                headers=self._get_auth_headers()
            )
        return self._client

    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"CampusAI-Service/{self.settings.app_version}"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def get_user_activities(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户历史活动"""
        try:
            response = await self.client.get(f"/users/{user_id}/activities")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 获取用户活动失败: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取用户活动异常: {e}")
            return None

    async def get_activity_details(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """获取活动详细信息"""
        try:
            response = await self.client.get(f"/activities/{activity_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 获取活动详情失败: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取活动详情异常: {e}")
            return None

    async def get_club_resources(self, club_id: str) -> Optional[Dict[str, Any]]:
        """获取社团资源信息"""
        try:
            response = await self.client.get(f"/clubs/{club_id}/resources")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 获取社团资源失败: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取社团资源异常: {e}")
            return None

    async def submit_evaluation_result(self, activity_id: str, evaluation_data: Dict[str, Any]) -> bool:
        """提交评估结果到Spring Boot"""
        try:
            response = await self.client.post(
                f"/activities/{activity_id}/evaluations",
                json=evaluation_data
            )
            response.raise_for_status()
            logger.info(f"✅ 评估结果提交成功: {activity_id}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 提交评估结果失败: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ 提交评估结果异常: {e}")
            return False

    async def test_connection(self) -> bool:
        """测试Spring Boot连接"""
        try:
            response = await self.client.get("/actuator/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Spring Boot连接测试失败: {e}")
            return False

    async def close(self):
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None