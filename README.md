# FederatedLearningBackend

联邦学习平台后端服务（FastAPI），为 `FederatedLearningWebFrontEnd` 提供统一 REST API。

当前项目以 **Mock 模式优先** 运行，目标是先保证前后端联调稳定，再逐步切换到真实数据库/FedLBE 引擎。

---

## 1. 项目作用与职责

后端主要负责：

- 提供前端页面所需的全部业务接口（仪表盘、任务、模型、客户端、数据质量、系统设置）
- 统一返回格式，减少前端处理复杂度
- 在 Mock 模式下返回可用于演示和联调的稳定数据
- 预留真实模式下对数据库、FedLBE WebSocket、StorageService 的集成能力

---

## 2. 技术栈

- 语言：Python 3.9+
- Web 框架：FastAPI
- 数据校验：Pydantic / pydantic-settings
- ASGI 服务：Uvicorn
- ORM（真实模式）：SQLAlchemy
- 数据库迁移：Alembic
- 认证：python-jose (JWT)
- 实时通信（预留）：websockets
- HTTP 客户端（预留）：httpx
- 日志：loguru

依赖文件：`requirements.txt`

---

## 3. 后端架构（代码实现）

### 3.1 分层结构

```text
app/
├── main.py                # FastAPI 入口、生命周期、CORS、健康检查
├── config.py              # 环境变量配置
├── database.py            # DB 引擎与会话（真实模式）
├── api/                   # 路由层（Controller）
├── schemas/               # 请求/响应数据模型
├── services/              # 业务层（当前默认映射到 MockService）
├── fedlbe/                # FedLBE 桥接（真实模式预留）
└── utils/                 # 工具与 Mock 数据开关
```

### 3.2 请求处理流程

1. 前端请求进入 `app/main.py` 注册的 `/api/*` 路由
2. `api/router.py` 分发到具体模块
3. 模块调用 `services` 中对应 Service
4. 返回统一结构：`{ code, message, data }`

### 3.3 Mock/真实模式说明

- Mock 模式开关：`MOCK_MODE` 环境变量（`true/false`）
- 当前 `services/__init__.py` 默认将 `JobService/ModelService/...` 映射到 `Mock*Service`
- 因此即使关闭 `MOCK_MODE`，你当前代码也仍是 Mock 服务优先；如需切到真实服务需修改 `services/__init__.py`

---

## 4. 运行与启动

### 4.1 环境要求

- Python 3.9+
- pip

### 4.2 安装依赖

```bash
cd /Users/tina/Documents/project/4.4bishe/FederatedLearningBackend
python3 -m pip install -r requirements.txt
```

### 4.3 Mock 模式启动（推荐）

```bash
MOCK_MODE=true python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

### 4.4 访问地址

- 服务根：`http://localhost:3000/`
- 健康检查：`http://localhost:3000/health`
- OpenAPI 文档：`http://localhost:3000/docs`
- ReDoc：`http://localhost:3000/redoc`

---

## 5. 配置说明（环境变量）

配置来源：`.env`（默认）与系统环境变量。

关键字段（`app/config.py`）：

- `APP_NAME`：应用名
- `APP_ENV`：环境（development/production）
- `DEBUG`：调试开关
- `HOST` / `PORT`：服务监听地址
- `DATABASE_URL`：数据库连接串（真实模式）
- `FEDLBE_WS_URL`：FedLBE WS 地址
- `STORAGE_URL`：StorageService 地址
- `JWT_SECRET_KEY` / `JWT_ALGORITHM` / `JWT_EXPIRATION_MINUTES`
- `CORS_ORIGINS`：允许跨域来源（JSON 数组字符串）
- `LOG_LEVEL`：日志级别

额外说明：`MOCK_MODE` 在 `app/utils/mock_data.py` 中读取，默认值 `true`。

---

## 6. 统一响应规范

除文件下载类接口外，接口统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

分页数据规范：

```json
{
  "records": [],
  "total": 24,
  "pageNo": 1,
  "pageSize": 10
}
```

---

## 7. 完整接口清单

基础前缀：`/api`

> 下述请求体字段来自 `app/schemas/*`，为当前代码实际定义。

### 7.1 健康与基础

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |

---

### 7.2 Dashboard 模块

前缀：`/api/dashboard`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/stats` | 仪表盘统计 |
| GET | `/clients` | 在线客户端列表 |
| GET | `/currentJob` | 当前任务进度 |
| GET | `/logs` | 实时日志 |
| GET | `/chart/{chart_type}` | 图表数据（`accuracy`/`loss`） |

---

### 7.3 Job Management 模块

前缀：`/api/job`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/list` | 任务分页列表 |
| GET | `/detail/{job_id}` | 任务详情 |
| POST | `/create` | 创建任务 |
| POST | `/abort/{job_id}` | 中止任务 |
| GET | `/logs/{job_id}` | 下载任务日志（txt） |
| GET | `/metrics/{job_id}` | 任务指标 |
| POST | `/upload-model/{job_id}` | 上传任务模型文件（`.py`） |

#### `POST /api/job/list` 请求体

```json
{
  "pageNo": 1,
  "pageSize": 10,
  "status": "running",
  "keyword": "FL-2023"
}
```

字段：

- `pageNo` number，默认 1
- `pageSize` number，默认 10
- `status` string，可选
- `keyword` string，可选

#### `POST /api/job/create` 请求体（`JobCreate`）

```json
{
  "name": "医学图像分割",
  "description": "任务描述",
  "jobType": "medical",
  "algorithm": "FedAvg算法",
  "totalRounds": 10,
  "config": {
    "modelArchitecture": "ResNet",
    "framework": "PyTorch",
    "dataset": "Medical",
    "batchSize": 32,
    "learningRate": 0.001,
    "optimizer": "Adam",
    "lossFunction": "CrossEntropy",
    "clients": 8,
    "minClients": 5,
    "maxClients": 8,
    "secureComm": true,
    "secureAgg": true,
    "differentialPrivacy": false,
    "clientFraction": 1.0,
    "localEpochs": 5,
    "scheduler": "random",
    "compression": null
  },
  "clientIds": ["client-1", "client-2"],
  "modelFileContent": null
}
```

---

### 7.4 Model Management 模块

前缀：`/api/model`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/list` | 模型分页列表 |
| GET | `/detail/{model_id}` | 模型详情 |
| POST | `/upload` | 上传模型文件 |
| GET | `/download/{model_id}` | 下载模型文件 |
| POST | `/validate/{model_id}` | 模型验证 |
| POST | `/comparison` | 模型对比（最多 2 个） |
| POST | `/delete/{model_id}` | 删除模型 |

#### `POST /api/model/list` 请求体

```json
{
  "pageNo": 1,
  "pageSize": 10,
  "keyword": "ResNet",
  "jobId": "FL-2023-001"
}
```

#### `POST /api/model/upload` 表单字段

- `file`：文件（必填）
- `name`：模型名（可选）
- `job_id`：关联任务 ID（可选）
- `framework`：默认 `PyTorch`
- `architecture`：可选

#### `POST /api/model/comparison` 请求体

```json
{
  "modelIds": ["model-1", "model-2"]
}
```

---

### 7.5 Client Management 模块

前缀：`/api/client`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/list` | 客户端分页列表 |
| GET | `/detail/{client_id}` | 客户端详情 |
| POST | `/add` | 添加客户端 |
| POST | `/delete/{client_id}` | 删除客户端 |
| POST | `/update/{client_id}` | 更新客户端 |
| POST | `/reconnect/{client_id}` | 重连客户端 |
| GET | `/online` | 在线客户端列表 |

#### `POST /api/client/list` 请求体

```json
{
  "pageNo": 1,
  "pageSize": 10,
  "status": "online",
  "keyword": "FL-CLIENT"
}
```

#### `POST /api/client/add` 请求体（`ClientCreate`）

```json
{
  "name": "边缘设备 #1",
  "deviceType": "Edge Server",
  "ipAddress": "192.168.1.105",
  "port": 50051,
  "fedlbePort": 8200,
  "gpu": "NVIDIA RTX A6000",
  "cpu": "Intel Core i7",
  "memory": "32 GB",
  "os": "Ubuntu 20.04"
}
```

`/update/{client_id}` 与 `add` 字段一致，但均为可选字段。

---

### 7.6 Data Quality 模块

前缀：`/api/dataQuality`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/stats` | 数据质量统计 |
| GET | `/nodes` | 3D 节点质量数据 |
| GET | `/distribution` | 质量分布 |
| POST | `/warnings` | 警告分页列表 |
| POST | `/report` | 生成并下载 PDF 报告 |

#### `POST /api/dataQuality/warnings` 请求体

```json
{
  "pageNo": 1,
  "pageSize": 10,
  "type": "critical"
}
```

---

### 7.7 Settings 模块

前缀：`/api/settings`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/get` | 获取设置 |
| POST | `/save` | 保存设置 |
| POST | `/testConnection` | 测试连接 |
| POST | `/user/add` | 添加用户 |
| POST | `/user/update/{user_id}` | 更新用户 |
| POST | `/user/delete/{user_id}` | 删除用户 |
| POST | `/reset` | 重置默认设置 |

#### `POST /api/settings/save` 请求体（`SettingsSave`）

可包含任意一个或多个配置块：

- `connection`: `adminApiEndpoint`, `port`, `protocol`, `certificate`
- `workspace`: `secureWorkspacePath`, `pocWorkspacePath`, `deploymentMode`
- `security`: `enableSecureComm`, `enableSecureAgg`, `enableDiffPrivacy`, `noiseLevel`, `clippingNorm`

#### `POST /api/settings/testConnection` 请求体

```json
{
  "adminApiEndpoint": "http://localhost",
  "port": 8200,
  "protocol": "http"
}
```

#### `POST /api/settings/user/add` 请求体

```json
{
  "username": "researcher1",
  "password": "password123",
  "email": "r1@example.com",
  "fullName": "Researcher One",
  "role": "viewer"
}
```

---

## 8. 与前端联调方式

如果前端使用 Vite（端口 8080）+ 代理：

- 前端 `baseURL` 使用 `/api`
- Vite 代理把 `/api` 转发到 `http://127.0.0.1:3000`
- **不要 rewrite 去掉 `/api`**

推荐联调顺序：

1. 启动后端：3000
2. 启动前端：8080
3. 浏览器 Network 确认请求落到 `http://127.0.0.1:3000/api/...`

---

## 9. 测试与验证

项目自带基础 API 测试：

```bash
cd /Users/tina/Documents/project/4.4bishe/FederatedLearningBackend
python3 -m pytest -q
```

---

## 10. 常见问题

### Q1：为什么后端启动了但前端还是显示前端 mock 数据？

A：前端可能开启了 `VITE_USE_MOCK=true`，请在前端 `.env.development` 中改为 `false` 并重启前端。

### Q2：为什么请求 404？

A：检查 Vite 代理是否错误 rewrite 了 `/api` 前缀。

### Q3：为什么说是“真实模式”但依然是 mock 数据？

A：当前 `app/services/__init__.py` 把服务类默认映射到了 MockService，需要手动切换为真实服务类。

---

## 11. 后续可扩展方向

- 在 `services/__init__.py` 增加按环境变量自动选择真实/Mock 服务
- 完整接入 PostgreSQL + Alembic + Repository 层
- 接入 FedLBE 真正训练链路（WS 消息、结果回写、任务状态机）
- 增加接口鉴权中间件与权限模型
- 增加指标监控与结构化日志
