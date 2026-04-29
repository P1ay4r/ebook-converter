"""
EBook Converter - FastAPI 应用入口
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.database import init_db
from app.core.redis import close_redis
from app.api.router import router as api_router
from app.utils.cleanup import periodic_cleanup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    # 启动时
    logger.info("正在初始化数据库...")
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.covers_dir, exist_ok=True)
    os.makedirs(settings.temp_dir, exist_ok=True)
    await init_db()
    logger.info("数据库初始化完成")

    # 启动定时清理任务
    cleanup_task = asyncio.create_task(periodic_cleanup())

    yield

    # 关闭时
    cleanup_task.cancel()
    await close_redis()
    logger.info("应用已关闭")


app = FastAPI(
    title="EBook Converter",
    description="电子书格式转换工具",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地部署场景允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router)

# 挂载前端静态文件（生产环境）
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    logger.info(f"前端静态文件已挂载: {frontend_dir}")
else:
    logger.info("前端静态目录不存在，仅 API 模式运行")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
