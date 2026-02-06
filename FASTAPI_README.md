# ShareSlide - 股票数据可视化展示系统 (FastAPI 版)

## 项目概述

ShareSlide 是一个基于 Python 的股票数据可视化展示系统，它从 akshare 接口获取实时股票数据，并将其转换为适用于 Slidev 播放的 Markdown 文件或 HTML 幻灯片。本项目已重构为 FastAPI Web API，支持远程访问和更灵活的部署方式。

### 核心功能
- 从 akshare 接口获取 A 股市场实时数据
- 数据处理和清洗，包括计算市盈率、市值排名、净利润等指标
- 生成多种类型的股票数据幻灯片（全市场概览、个股详情、新闻资讯等）
- 支持缓存机制，避免重复请求数据
- 使用 Jinja2 模板引擎渲染 HTML 幻灯片
- 集成 ECharts 图表展示功能
- 提供 RESTful API 接口，支持远程调用

### 技术栈
- **Python 3.13.7+**: 主要编程语言
- **FastAPI**: 现代高性能 Web 框架
- **AkShare**: 金融数据获取库
- **Jinja2**: 模板引擎
- **Pandas**: 数据处理和分析
- **Loguru**: 日志记录
- **Reveal.js**: HTML 幻灯片框架
- **ECharts**: 数据可视化图表库
- **Pydantic**: 数据验证和设置管理

## 安装与运行

### 环境要求
- Python 3.13.7 或更高版本
- uv 包管理器（推荐）

### 安装步骤

1. **克隆项目并进入目录**
```bash
git clone <repository-url>
cd shareslide
```

2. **创建虚拟环境并安装依赖**
```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

uv sync
```

3. **运行 FastAPI 服务器**
```bash
# 方式一：使用 uvicorn 直接运行
uvicorn api.main:app --reload --port 8000

# 方式二：使用项目脚本
python run_api.py

# 方式三：使用命令行工具
shareslide-api
```

## API 接口说明

### 数据接口

#### 获取市场概要
```
GET /api/data/market-summary
```
获取当前市场的总体情况，包括总股票数、总成交额、涨跌幅分布等。

#### 获取所有股票数据
```
GET /api/data/stocks
```
获取所有股票的基本数据（限制返回前100条）。

#### 获取特定股票详情
```
GET /api/data/stocks/{symbol}
```
获取特定股票的详细信息，例如：
```
GET /api/data/stocks/600674
```

### 幻灯片接口

#### 生成个股幻灯片
```
POST /api/slides/generate
Content-Type: application/json

{
  "stock_codes": ["600674", "300750"],
  "template_type": "table",
  "title": "Custom Stock Slides"
}
```
根据指定的股票代码生成幻灯片。

#### 生成市场概要幻灯片
```
POST /api/slides/market-summary?filename=market_overview
```
生成市场概要幻灯片。

#### 获取示例股票代码
```
GET /api/slides/sample-codes
```
获取预设的示例股票代码列表。

## 主要改进

### 1. Web API 接口
- 将原来的 CLI 应用转换为 Web API，支持远程访问
- 提供 RESTful 接口，便于与其他系统集成

### 2. 自动化文档
- FastAPI 自动生成交互式 API 文档
- 访问 `/docs` 或 `/redoc` 查看 API 文档

### 3. 类型安全
- 使用 Pydantic 模型进行请求/响应数据验证
- 提高代码的健壮性和可维护性

### 4. 异步性能
- FastAPI 的异步特性提高了并发处理能力
- 更好地处理大量数据请求

### 5. 模块化架构
- 清晰的分层架构（路由、服务、模型、配置）
- 便于维护和扩展

## 使用场景

### Web 应用集成
- 可以轻松集成到 Web 应用中
- 通过 API 调用生成股票数据幻灯片

### 自动化报告
- 支持定时任务自动生成市场报告
- 可与其他系统集成实现自动化数据展示

### 远程访问
- 支持远程访问股票数据
- 便于分布式部署和使用

## 配置

项目支持通过环境变量进行配置：

```bash
# .env 文件示例
DEBUG=true
CACHE_DIR=cache
REVEAL_OUTPUT_DIR=reveal
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

## 部署

### 本地开发
```bash
python run_api.py
```

### 生产环境
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

或者使用容器化部署：
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .
RUN pip install uv && uv sync

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 故障排除

如果遇到问题，请检查：

1. 网络连接是否正常（数据获取需要网络）
2. Python 版本是否符合要求（3.13.7+）
3. 依赖包是否正确安装
4. 查看日志输出以获取详细错误信息
5. 访问 `/health` 端点检查服务状态

对于数据获取失败的问题，可能是由于 akshare 接口限制或网络问题，稍后再试通常可以解决。
