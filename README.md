# Point Cloud Filter Intent Parser

一个基于 FastAPI 的后端服务，用于将自然语言描述转换为点云过滤参数 JSON。该服务适用于点云处理场景中，用户通过文本命令描述过滤需求，例如“高度超过 10 米”或“裁剪一个 20x20x20 的区域”，系统可自动解析为结构化过滤条件，供上层业务调用。

## 项目简介

本项目提供了一个轻量、可扩展的接口，用于将自然语言意图转成机器可理解的过滤配置，减少前端或调用方手工拼接 JSON 的成本。服务内部通过 DeepSeek 模型解析文本，并将结果限制为标准 JSON 结构，便于接入点云编辑器、可视化平台或后端数据处理流程。

### 主要能力

- 解析自然语言点云过滤意图
- 支持高度过滤与区域裁剪过滤
- 返回结构化 JSON 结果
- 提供健康检查接口
- 支持 CORS，便于前端直接调用

## 技术栈

- Python 3.10+
- FastAPI
- Pydantic
- OpenAI Python SDK
- DeepSeek Chat API
- python-dotenv
- Uvicorn

## 项目结构

```text
backend/
├── main.py              # FastAPI 应用入口和接口实现
├── requirements.txt     # 依赖列表
├── pyproject.toml       # 项目元数据与依赖声明
├── README.md            # 项目说明文档
└── .env                 # 本地环境变量（未跟踪）
```

## 功能说明

### 1. 自然语言解析接口

通过 POST /parse 接口，传入用户的自然语言描述，服务会调用大模型解析，并返回过滤规则 JSON。

#### 支持的过滤类型

1. 按高度过滤

```json
{"filter": {"minHeight": 10}}
```

2. 按区域裁剪

```json
{"filter": {"clipBox": {"size": [20, 20, 20], "position": [0, 0, 0]}}}
```

#### 解析规则

- 用户说：“高度超过 10 米” → `{"filter": {"minHeight": 10}}`
- 用户说：“裁剪一个 20x20x20 的区域” → `{"filter": {"clipBox": {"size": [20,20,20], "position": [0,0,0]}}}`
- 如果无法识别，则返回：

```json
{"filter": null}
```

### 2. 健康检查接口

GET /health 返回服务状态，便于部署后的监控与探测。

```json
{"status": "ok"}
```

## 快速开始

### 1. 安装 Python 依赖

推荐使用 Python 3.10 及以上版本。

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

或者使用项目中声明的 pyproject 配置：

```bash
pip install .
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，设置 DeepSeek API Key：

```env
KEY=your_deepseek_api_key
```

> 说明：当前代码中使用 `os.getenv("KEY")` 读取环境变量，因此必须确保该值已正确配置。

### 3. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，默认可访问：

- http://localhost:8000/docs
- http://localhost:8000/redoc

## API 接口说明

### POST /parse

#### 请求体

```json
{
  "query": "高度超过 10 米"
}
```

#### 响应示例

```json
{
  "filter": {
    "minHeight": 10
  }
}
```

#### 错误处理

如果模型调用失败或无法解析，接口会返回：

```json
{
  "filter": null,
  "error": "..."
}
```

### GET /health

```json
{
  "status": "ok"
}
```

## 示例调用

### 使用 curl

```bash
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{"query":"裁剪一个 20x20x20 的区域"}'
```

返回：

```json
{
  "filter": {
    "clipBox": {
      "size": [20, 20, 20],
      "position": [0, 0, 0]
    }
  }
}
```

## 设计思路

该服务的核心价值在于把“自然语言语义理解”与“结构化过滤配置生成”解耦。业务方只需提交描述性指令，后端即可通过大语言模型完成解析，并返回统一格式的过滤参数，减少上下游接口的耦合度，提高开发效率。

从架构上看，服务本身保持了极简设计：

- 入口层：FastAPI 接口
- 解析层：DeepSeek 模型
- 数据校验层：Pydantic BaseModel
- 结果层：JSON 输出

这使得它非常适合作为较小规模的 AI 能力服务，也便于后续扩展为更复杂的点云处理指令编排系统。

## 注意事项

- 该服务依赖 DeepSeek API，因此网络连接和 API Key 配置必须正常。
- 由于模型解析会受到描述方式影响，建议对输入语句保持简洁、规范和稳定结构。
- 如果侧重稳定性，可在生产环境中增加更严格的输入校验和错误重试机制。

## 未来扩展建议

- 增加更多过滤类型，如按颜色、按密度、按类别筛选
- 增加多轮对话上下文支持
- 为接口增加鉴权与限流策略
- 将响应格式统一到更正式的 API schema 定义
- 增加日志监控和调用链追踪

## 许可证

本项目当前未声明具体许可证，适用于内部开发或个人学习场景。如需用于正式商业发布，建议在发布前补充明确的开源协议。

## 结语

本项目提供了一个简单但实用的 AI 辅助点云过滤解析服务，适合在点云处理、3D 场景编辑以及数据筛选等业务中快速接入自然语言交互能力。通过结构化输出，调用方可以更方便地将自然语言指令转成真实的过滤参数，实现从“描述”到“执行”的闭环。
