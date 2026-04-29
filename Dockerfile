# ---- 构建阶段：前端 ----
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ---- 构建阶段：后端依赖 ----
FROM python:3.12-slim AS backend-deps

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- 运行阶段 ----
FROM python:3.12-slim

# 安装 calibre
RUN apt-get update && apt-get install -y --no-install-recommends \
    calibre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制 Python 依赖
COPY --from=backend-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 创建存储目录
RUN mkdir -p /app/storage/{uploads,output,covers,temp}

EXPOSE 80

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "80"]
