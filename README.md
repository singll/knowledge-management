# Knowledge Management System

基于 Flask + Vue3 的知识管理系统，集成 RagFlow、数据源管理、RSS 订阅和 n8n Webhook 工作流。

## 📋 功能特性

### 1. RagFlow 文档管理
- ✅ 字符串内容直接上传到 RagFlow 知识库
- ✅ 批量上传多个文档
- ✅ 文档列表查询和管理
- ✅ 文档解析状态追踪
- ✅ 支持多种解析器（naive、general、paper、book）

### 2. 数据源管理
- ✅ 管理技术文章、资讯网站等数据源
- ✅ 支持分类（技术、新闻、博客等）
- ✅ 标签关联和筛选
- ✅ 启用/禁用状态管理

### 3. RSS 订阅管理
- ✅ RSS 订阅源的增删改查
- ✅ 分类和标签管理
- ✅ 最后抓取时间记录

### 4. 标签系统
- ✅ 统一的标签管理
- ✅ 自定义标签颜色
- ✅ 跨模块标签关联

### 5. Webhook 工作流
- ✅ 配置多个 n8n Webhook
- ✅ 手动触发工作流（输入文章链接）
- ✅ 调用历史记录和详情
- ✅ 支持自定义额外数据
- ✅ 状态监控（成功/失败/等待中）

## 🛠 技术栈

### 后端
- **Python 3.11+**
- **Flask 3.0** - Web 框架
- **SQLAlchemy** - ORM
- **SQLite** - 数据库
- **uv** - 包管理工具
- **Gunicorn** - WSGI 服务器

### 前端
- **Vue 3.4** - 前端框架
- **Vite 5.2** - 构建工具
- **Element Plus 2.6** - UI 组件库
- **Pinia 2.1** - 状态管理
- **Axios 1.6** - HTTP 客户端
- **pnpm 9.15** - 包管理工具

### 部署
- **Docker & Docker Compose**
- **Nginx** - 反向代理

## 📦 项目结构

```
knowledge-management/
├── backend/                    # Flask 后端
│   ├── app/
│   │   ├── __init__.py        # 应用工厂
│   │   ├── config.py          # 配置管理
│   │   ├── models.py          # 数据库模型
│   │   ├── extensions.py      # 扩展初始化
│   │   ├── api/               # API 路由
│   │   │   ├── ragflow.py     # RagFlow API
│   │   │   ├── datasource.py  # 数据源 API
│   │   │   ├── rss.py         # RSS API
│   │   │   ├── tags.py        # 标签 API
│   │   │   └── webhook.py     # Webhook API
│   │   ├── services/          # 业务逻辑
│   │   │   ├── ragflow_service.py
│   │   │   └── webhook_service.py
│   │   └── utils/             # 工具函数
│   │       └── response.py
│   ├── pyproject.toml         # uv 项目配置
│   ├── .python-version        # Python 版本
│   ├── Dockerfile
│   └── run.py                 # 启动入口
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/               # API 调用
│   │   ├── views/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   ├── utils/             # 工具函数
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json           # pnpm 配置（版本锁定）
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd knowledge-management
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入 RagFlow API Key
nano .env
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端界面：http://localhost:8080
- 后端 API：http://localhost:5000
- 健康检查：http://localhost:5000/health

### 方式二：本地开发

#### 后端开发

```bash
cd backend

# 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 配置环境变量
export RAGFLOW_URL=http://localhost:9380
export RAGFLOW_API_KEY=your-api-key

# 启动开发服务器
python run.py
```

#### 前端开发

```bash
cd frontend

# 安装 pnpm（如果未安装）
npm install -g pnpm@9.15.0

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

访问 http://localhost:8080

## 🔧 配置说明

### RagFlow 配置

1. 获取 RagFlow API Key：
   - 登录 RagFlow 管理界面
   - 进入设置 → API Keys
   - 创建新的 API Key

2. 配置环境变量：
```bash
RAGFLOW_URL=http://your-ragflow-host:9380
RAGFLOW_API_KEY=your-api-key-here
```

### n8n Webhook 配置

1. 在 n8n 中创建工作流
2. 添加 Webhook 触发器节点
3. 复制 Webhook URL
4. 在系统中添加 Webhook 配置

## 📝 API 文档

### RagFlow API

#### 上传字符串
```http
POST /api/ragflow/upload/string
Content-Type: application/json

{
  "dataset_id": "xxx",
  "content": "文档内容",
  "filename": "document.md",
  "parser_id": "naive",
  "run": "1",
  "wait_for_completion": false
}
```

#### 列出文档
```http
GET /api/ragflow/documents?dataset_id=xxx&page=1&page_size=20
```

#### 删除文档
```http
DELETE /api/ragflow/documents
Content-Type: application/json

{
  "dataset_id": "xxx",
  "document_id": "xxx"
}
```

### 标签 API

#### 获取标签列表
```http
GET /api/tags?page=1&per_page=20&keyword=搜索关键词
```

#### 创建标签
```http
POST /api/tags
Content-Type: application/json

{
  "name": "标签名称",
  "description": "描述",
  "color": "#409EFF"
}
```

#### 更新标签
```http
PUT /api/tags/{tag_id}
Content-Type: application/json

{
  "name": "新名称",
  "description": "新描述"
}
```

#### 删除标签
```http
DELETE /api/tags/{tag_id}
```

### 数据源 API

#### 获取数据源列表
```http
GET /api/datasources?page=1&per_page=20&category=tech&is_active=true
```

#### 创建数据源
```http
POST /api/datasources
Content-Type: application/json

{
  "name": "数据源名称",
  "url": "https://example.com",
  "type": "website",
  "category": "tech",
  "description": "描述",
  "is_active": true,
  "tag_ids": [1, 2, 3]
}
```

#### 更新数据源
```http
PUT /api/datasources/{datasource_id}
Content-Type: application/json

{
  "name": "新名称",
  "is_active": false
}
```

#### 删除数据源
```http
DELETE /api/datasources/{datasource_id}
```

### RSS API

#### 获取 RSS 列表
```http
GET /api/rss?page=1&per_page=20&category=tech
```

#### 创建 RSS 订阅
```http
POST /api/rss
Content-Type: application/json

{
  "name": "订阅源名称",
  "url": "https://example.com/feed.xml",
  "category": "tech",
  "description": "描述",
  "is_active": true,
  "tag_ids": [1, 2]
}
```

#### 更新 RSS 订阅
```http
PUT /api/rss/{rss_id}
Content-Type: application/json

{
  "name": "新名称",
  "is_active": false
}
```

#### 删除 RSS 订阅
```http
DELETE /api/rss/{rss_id}
```

### Webhook API

#### 获取 Webhook 配置列表
```http
GET /api/webhooks/configs?page=1&per_page=20&is_active=true
```

#### 创建 Webhook 配置
```http
POST /api/webhooks/configs
Content-Type: application/json

{
  "name": "保存文章到知识库",
  "url": "https://n8n.example.com/webhook/xxx",
  "method": "POST",
  "description": "描述",
  "is_active": true
}
```

#### 触发 Webhook
```http
POST /api/webhooks/trigger
Content-Type: application/json

{
  "webhook_id": 1,
  "article_url": "https://example.com/article",
  "extra_data": {
    "tags": ["tech", "ai"]
  }
}
```

#### 获取调用历史
```http
GET /api/webhooks/history?page=1&per_page=20&webhook_id=1&status=success
```

## 🔍 使用场景

### 场景 1：自动保存文章到知识库

1. 在 n8n 中创建工作流：
   - Webhook 触发器接收文章链接
   - HTTP Request 节点抓取文章内容
   - 调用 RagFlow API 保存到知识库

2. 在系统中配置 Webhook

3. 在界面上输入文章链接，触发工作流

### 场景 2：管理技术资讯源

1. 创建标签：Python、AI、前端等

2. 添加数据源：
   - Hacker News
   - Reddit Programming
   - Medium Technology

3. 关联标签，方便分类筛选

### 场景 3：RSS 订阅聚合

1. 添加 RSS 订阅源

2. 在 n8n 中创建定时工作流：
   - 定时触发
   - 调用系统 API 获取 RSS 列表
   - 抓取最新文章
   - 保存到 RagFlow

## 📊 数据库结构

### 表结构

- **tags** - 标签表
- **data_sources** - 数据源表
- **rss_feeds** - RSS 订阅源表
- **webhook_configs** - Webhook 配置表
- **webhook_history** - Webhook 调用历史表
- **datasource_tags** - 数据源-标签关联表
- **rss_tags** - RSS-标签关联表

## 🐛 故障排查

### 后端无法连接 RagFlow

1. 检查 `RAGFLOW_URL` 是否正确
2. 检查 `RAGFLOW_API_KEY` 是否有效
3. 确保网络可达：`curl http://ragflow-host:9380/health`

### 前端无法访问后端 API

1. 检查后端是否启动：`curl http://localhost:5000/health`
2. 检查 CORS 配置
3. 查看浏览器控制台错误信息

### Docker 容器无法启动

1. 查看日志：`docker-compose logs backend`
2. 检查端口占用：`netstat -tuln | grep 5000`
3. 检查环境变量配置

### 数据库文件权限问题

```bash
# 修复权限
sudo chown -R 1000:1000 backend/data
sudo chmod -R 755 backend/data
```

## 🔄 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 初始版本发布
- ✅ RagFlow 文档管理
- ✅ 数据源和 RSS 管理
- ✅ 标签系统
- ✅ Webhook 工作流集成
- ✅ Docker 部署支持

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**注意事项：**

1. 生产环境请修改 `SECRET_KEY`
2. 建议使用 HTTPS 部署
3. 定期备份 SQLite 数据库文件
4. RagFlow API Key 请妥善保管
5. n8n Webhook URL 建议添加认证