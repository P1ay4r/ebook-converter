# EBook Converter - 电子书格式转换工具

基于 **FastAPI + React + calibre** 的 Web 端电子书格式转换工具，支持 10 种格式互转、批量处理、元数据编辑、实时进度推送。可 Docker 一键部署，也可本地开发模式运行。

---

## 支持的格式

| 格式 | 说明 | 输入 | 输出 |
|------|------|:----:|:----:|
| EPUB | 国际标准开放电子书格式 | ✅ | ✅ |
| MOBI | Kindle 旧格式 | ✅ | ✅ |
| AZW3 | Kindle 新格式 (KF8) | ✅ | ✅ |
| PDF | 便携式文档格式 | ✅ | ✅ |
| TXT | 纯文本 | ✅ | ✅ |
| DOCX | Microsoft Word 格式 | ✅ | ✅ |
| HTML | 网页格式 | ✅ | ✅ |
| FB2 | FictionBook 格式 | ✅ | ✅ |
| CBZ | ZIP 打包的漫画 | ✅ | ✅ |
| CBR | RAR 打包的漫画 | ✅ | ✅ |

---

## 环境要求

### 生产部署（Docker）

| 依赖 | 版本要求 | 获取方式 |
|------|---------|---------|
| Docker | 20.10+ | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Docker Compose | v2+ | 通常随 Docker Desktop 一起安装 |

### 开发模式

| 依赖 | 版本要求 | 获取方式 |
|------|---------|---------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| calibre | 7.x | [calibre-ebook.com](https://calibre-ebook.com/download) |

### calibre 安装说明

转换引擎依赖 calibre，**必须安装**才能执行实际格式转换。

**Windows：**
```bash
# 从官网下载安装包，或使用 winget
winget install calibre
```
安装后确保 `ebook-convert.exe` 在系统 PATH 中（安装程序通常会自动添加）。

**macOS：**
```bash
brew install calibre
```

**Linux (Ubuntu/Debian)：**
```bash
sudo apt-get update && sudo apt-get install -y calibre
```

**验证安装：**
```bash
ebook-convert --version
# 输出: calibre (calibre 7.x) ...
```

> 如果未安装 calibre，API 仍然可以启动，但转换任务会返回错误。前端在转换时也会有相应提示。

---

## 快速启动

### 方式一：Docker 部署（推荐）

```bash
# 1. 进入项目目录
cd ebook-converter

# 2. 启动所有服务
docker compose up --build

# 3. 打开浏览器访问
open http://localhost:8080
```

Docker 镜像已内置 calibre，无需额外安装。

### 方式二：开发模式

需要先安装 Python 和 Node.js 依赖。

#### 1. 启动后端

```bash
cd ebook-converter/backend

# 安装依赖（推荐在虚拟环境中）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动 API 服务
uvicorn app.main:app --reload --port 8000
```

后端默认运行在 http://localhost:8000

自动创建 API 文档：
- OpenAPI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 2. 启动前端（新开终端）

```bash
cd ebook-converter/frontend

npm install
npm run dev -- --port 5173
```

前端默认运行在 http://localhost:5173

> 开发模式下，前端的 `/api` 请求会自动代理到后端 `localhost:8000`。

#### 3. 启动 Worker（可选，任务队列用）

如果需要异步转换任务和实时进度推送：

```bash
# 需要先启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 启动 Celery Worker
cd ebook-converter/backend
celery -A app.worker.app worker --concurrency=4 --loglevel=info
```

> 不启动 Worker 时，转换任务会直接提交但无法异步执行。最小可用模式下可以不启动 Redis 和 Worker。

---

## 项目结构

```
ebook-converter/
├── docker-compose.yml          # Docker 编排（app + worker + redis）
├── Dockerfile                  # 多阶段构建（含 calibre + 前端）
├── .env.example                # 环境变量模板
│
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 应用入口 + 生命周期管理
│   │   ├── config.py           # 配置（环境变量读取）
│   │   ├── api/                # API 路由
│   │   │   ├── files.py        # 文件上传/下载/删除
│   │   │   ├── conversion.py   # 转换任务管理
│   │   │   ├── metadata.py     # 元数据 CRUD
│   │   │   └── ws.py           # WebSocket 实时推送
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   ├── worker/             # Celery 任务 + calibre 封装
│   │   └── core/               # 基础设施（DB/Redis/存储）
│   └── requirements.txt
│
├── frontend/                   # React + Vite 前端
│   ├── src/
│   │   ├── pages/              # 页面
│   │   ├── components/         # UI 组件（上传/转换/元数据）
│   │   ├── hooks/              # WebSocket hook
│   │   ├── api/                # API 客户端
│   │   └── types/              # TypeScript 类型定义
│   └── package.json
│
└── nginx/                      # Nginx 配置（生产用）
```

---

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/files/upload` | 上传文件 |
| GET | `/api/v1/files` | 文件列表 |
| GET | `/api/v1/files/{id}` | 文件详情 |
| DELETE | `/api/v1/files/{id}` | 删除文件 |
| GET | `/api/v1/files/{id}/download` | 下载文件 |
| GET | `/api/v1/files/{id}/cover` | 获取封面 |
| GET | `/api/v1/files/formats/all` | 支持的格式列表 |
| POST | `/api/v1/conversion/start` | 提交转换任务 |
| GET | `/api/v1/conversion/task/{id}` | 查询任务进度 |
| GET | `/api/v1/conversion/batch/{id}` | 查询批量任务进度 |
| POST | `/api/v1/conversion/task/{id}/cancel` | 取消任务 |
| GET | `/api/v1/metadata/{file_id}` | 获取元数据 |
| PUT | `/api/v1/metadata/{file_id}` | 更新元数据 |
| POST | `/api/v1/metadata/{file_id}/cover` | 上传封面 |
| WS | `/api/v1/ws/task/{task_id}` | WebSocket 实时进度 |
| GET | `/health` | 健康检查 |

---

## 配置说明

通过环境变量配置（参见 `.env.example`）：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `REDIS_URL` | `redis://redis:6379/0` | Redis 连接地址 |
| `DATABASE_URL` | `sqlite+aiosqlite:///data/app.db` | 数据库连接地址 |
| `CONCURRENT_WORKERS` | `4` | 并行转换 Worker 数量 |
| `FILE_MAX_SIZE` | `209715200` (200MB) | 文件大小上限 |
| `FILE_TTL_HOURS` | `24` | 文件保留时间（小时后自动清理） |
| `STORAGE_DIR` | `/app/storage` | 文件存储根目录 |

---

## 使用注意事项

### 文件管理

- 上传文件大小上限为 **200MB**（可通过 `FILE_MAX_SIZE` 调整）
- 文件默认保留 **24 小时**后自动清理（可通过 `FILE_TTL_HOURS` 调整）
- 相同内容的文件（基于 SHA256）会自动去重，不会重复上传
- 批量上传最多 50 个文件

### 格式转换

- **PDF → 其他格式**：PDF 是固定排版格式，转换后排版结构可能发生变化，尤其是多栏、表格、复杂排版
- **CBZ/CBR**：仅支持转换为 PDF，不支持输出为其他格式
- **TXT 转换**：纯文本没有排版信息，转换为 EPUB/MOBI 等格式时排版从默认样式
- 转换超时限制为 **10 分钟**，超大文件转换失败时建议降低质量参数

### 性能建议

- 4 核 CPU 建议 `CONCURRENT_WORKERS=3`
- 8 核 CPU 建议 `CONCURRENT_WORKERS=6`
- 磁盘建议保留至少 **10GB** 可用空间用于临时文件
- Docker 部署时建议将存储目录挂载到宿主机持久化卷

### 安全

- 本项目为本地部署设计，**不包含用户认证系统**
- 所有文件处理在本地完成，**不会上传到任何第三方服务**
- 如需暴露到公网，建议前置 Nginx 反向代理 + 访问控制

### 常见问题

**Q: 转换后排版错乱怎么办？**
> 尝试使用"高级选项"中的"移除段落间距"和"自定义 CSS"来调整输出样式。

**Q: 转换进度卡住不动？**
> 检查是否启动了 Celery Worker，以及 Redis 是否正常运行。开发模式下 Worker 不是必须的，但实时进度推送依赖 WebSocket + Redis。

**Q: Docker 构建失败？**
> 确保 Docker Desktop 已启动且版本 ≥ 20.10。首次构建需要下载 calibre 安装包，耗时可能较长（3-10 分钟）。

**Q: 支持批量下载吗？**
> 批量转换完成后，所有成功转换的文件会分组展示，每个文件可单独下载。目前暂未支持 ZIP 打包批量下载。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 转换引擎 | calibre `ebook-convert` |
| 后端框架 | Python FastAPI |
| 异步任务 | Celery + Redis |
| 数据库 | SQLite (可通过 SQLAlchemy 切换到 PostgreSQL) |
| 前端 | React + TypeScript + Vite + Tailwind CSS |
| 部署 | Docker + Docker Compose |

---

## License

本项目基于 GPLv3 许可证开源（因依赖 calibre）。
