import os
import uuid
import aiofiles
from pathlib import Path
from datetime import datetime

from app.config import settings


class FileStorage:
    """文件存储抽象，管理上传/输出文件的磁盘读写。"""

    @staticmethod
    def _ensure_dir(dir_path: str):
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _date_prefix() -> str:
        return datetime.utcnow().strftime("%Y-%m-%d")

    async def save_upload(self, file_data: bytes, ext: str) -> str:
        """保存上传文件，返回相对存储路径。"""
        date_str = self._date_prefix()
        dir_path = os.path.join(settings.upload_dir, date_str)
        self._ensure_dir(dir_path)

        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(dir_path, filename)
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(file_data)
        return filepath

    async def save_output(self, temp_path: str, ext: str) -> str:
        """将转换结果移动到存储目录，返回路径。"""
        date_str = self._date_prefix()
        dir_path = os.path.join(settings.output_dir, date_str)
        self._ensure_dir(dir_path)

        filename = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(dir_path, filename)
        os.rename(temp_path, dest)
        return dest

    async def save_cover(self, file_data: bytes) -> str:
        """保存封面图片。"""
        self._ensure_dir(settings.covers_dir)
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(settings.covers_dir, filename)
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(file_data)
        return filepath

    async def delete_file(self, filepath: str):
        """删除文件，不存在时静默忽略。"""
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

    def get_absolute_path(self, filepath: str) -> str:
        """获取文件的绝对路径。"""
        if os.path.isabs(filepath):
            return filepath
        return os.path.join(settings.storage_dir, filepath)

    @staticmethod
    def file_exists(filepath: str) -> bool:
        return os.path.isfile(filepath)


storage = FileStorage()
