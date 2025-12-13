# 使用 uv 官方镜像
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# 复制项目文件
COPY pyproject.toml .python-version ./
COPY app ./app
COPY run.py ./

# 安装依赖
RUN uv pip install --system --no-cache .

# 最终镜像
FROM python:3.11-slim-bookworm

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 复制已安装的包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
WORKDIR /app
COPY --from=builder /app ./

# 创建数据目录
RUN mkdir -p /app/data /tmp/ragflow_uploads && \
    chmod 777 /app/data /tmp/ragflow_uploads

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

EXPOSE 5000

# 使用 gunicorn 运行
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", \
     "--access-logfile", "-", "--error-logfile", "-", "run:app"]
