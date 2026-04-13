import oss2
from typing import Optional, List, BinaryIO
from loguru import logger
from ..core.config import get_settings

class OSSClient:
    """阿里云OSS客户端封装"""

    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._bucket = None

    @property
    def bucket(self):
        """获取OSS存储桶（懒加载）"""
        if self._bucket is None:
            self._connect()
        return self._bucket

    def _connect(self):
        """连接OSS"""
        try:
            auth = oss2.Auth(
                self.settings.oss_access_key_id,
                self.settings.oss_access_key_secret
            )
            self._bucket = oss2.Bucket(
                auth,
                self.settings.oss_endpoint,
                self.settings.oss_bucket_name
            )
            logger.info(f"✅ OSS连接成功: {self.settings.oss_bucket_name}")
        except Exception as e:
            logger.error(f"❌ OSS连接失败: {e}")
            raise

    async def upload_model(self, model_type: str, version: str, model_data: bytes) -> bool:
        """上传模型到OSS"""
        try:
            object_key = f"{self.settings.oss_model_prefix}{model_type}/{version}.pkl"
            result = self.bucket.put_object(object_key, model_data)
            logger.info(f"✅ 模型上传成功: {object_key} (ETag: {result.etag})")
            return True
        except Exception as e:
            logger.error(f"❌ 模型上传失败: {e}")
            return False

    async def download_model(self, model_type: str, version: str) -> Optional[bytes]:
        """从OSS下载模型"""
        try:
            object_key = f"{self.settings.oss_model_prefix}{model_type}/{version}.pkl"
            result = self.bucket.get_object(object_key)
            model_data = result.read()
            logger.info(f"✅ 模型下载成功: {object_key} (大小: {len(model_data)} bytes)")
            return model_data
        except oss2.exceptions.NoSuchKey:
            logger.warning(f"⚠️  模型不存在: {model_type}/{version}")
            return None
        except Exception as e:
            logger.error(f"❌ 模型下载失败: {e}")
            return None

    async def list_model_versions(self, model_type: str) -> List[str]:
        """列出指定模型类型的所有版本"""
        try:
            prefix = f"{self.settings.oss_model_prefix}{model_type}/"
            result = oss2.ObjectIterator(self.bucket, prefix=prefix)

            versions = []
            for obj in result:
                # 从对象键中提取版本号
                filename = obj.key.split('/')[-1]
                if filename.endswith('.pkl'):
                    version = filename[:-4]  # 移除.pkl后缀
                    versions.append(version)

            # 按时间戳排序（降序）
            versions.sort(reverse=True)
            return versions

        except Exception as e:
            logger.error(f"❌ 列出模型版本失败: {e}")
            return []

    async def delete_model(self, model_type: str, version: str) -> bool:
        """删除OSS上的模型"""
        try:
            object_key = f"{self.settings.oss_model_prefix}{model_type}/{version}.pkl"
            self.bucket.delete_object(object_key)
            logger.info(f"✅ 模型删除成功: {object_key}")
            return True
        except Exception as e:
            logger.error(f"❌ 模型删除失败: {e}")
            return False

    def test_connection(self) -> bool:
        """测试OSS连接"""
        try:
            # 尝试列出存储桶中的对象（限制1个）
            result = oss2.ObjectIterator(self.bucket, max_keys=1)
            list(result)  # 触发迭代
            return True
        except Exception as e:
            logger.error(f"❌ OSS连接测试失败: {e}")
            return False