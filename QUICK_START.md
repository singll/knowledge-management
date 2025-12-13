# 快速开始指南

## 5 分钟快速部署

### 1. 准备工作

确保已安装：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 克隆项目

```bash
git clone <repository-url>
cd knowledge-management
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置（必须填写 RagFlow API Key）
nano .env
```

最小配置：
```bash
RAGFLOW_URL=http://your-ragflow-host:9380
RAGFLOW_API_KEY=your-api-key-here
```

### 4. 启动服务

```bash
docker-compose up -d
```

### 5. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查后端健康
curl http://localhost:5000/health

# 访问前端
open http://localhost:8080
```

## 本地开发模式

### 后端开发

```bash
cd backend

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 配置环境变量
export RAGFLOW_URL=http://localhost:9380
export RAGFLOW_API_KEY=your-key
export FLASK_DEBUG=true

# 启动
python run.py
```

### 前端开发

```bash
cd frontend

# 安装 pnpm
npm install -g pnpm@9.15.0

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

## 常用命令

### Docker 管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 重新构建
docker-compose up -d --build
```

### 数据库管理

```bash
# 进入后端容器
docker-compose exec backend bash

# 查看数据库
sqlite3 /app/data/knowledge.db

# 备份数据库
docker-compose exec backend cp /app/data/knowledge.db /app/data/backup_$(date +%Y%m%d).db
```

## 首次使用

### 1. 创建标签

访问 http://localhost:8080/tags

- 点击"新建标签"
- 输入标签名称（如：Python、AI、前端）
- 选择颜色
- 保存

### 2. 添加数据源

访问 http://localhost:8080/datasources

- 点击"新建数据源"
- 填写名称和 URL
- 选择分类和标签
- 保存

### 3. 配置 Webhook

访问 http://localhost:8080/webhook

- 点击"新建配置"
- 输入名称和 n8n Webhook URL
- 保存

### 4. 测试上传

访问 http://localhost:8080/ragflow

- 输入 Dataset ID
- 填写文档内容
- 点击上传

## 故障排查

### 端口冲突

```bash
# 修改端口（编辑 docker-compose.yml）
ports:
  - "5001:5000"  # 后端
  - "8081:80"    # 前端
```

### 权限问题

```bash
# 修复数据目录权限
sudo chown -R $USER:$USER backend/data
```

### 网络问题

```bash
# 检查 Docker 网络
docker network ls
docker network inspect knowledge-management_knowledge-net
```

## 下一步

- 阅读完整文档：[README.md](README.md)
- 查看 API 文档：访问 http://localhost:5000/health
- 配置 n8n 工作流
- 开始管理你的知识库！