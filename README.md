# Context7 MCP 服务器 - Python 版本

这是 Context7 MCP 服务器的 Python 实现，提供最新的库文档和代码示例。

## 功能特点

- 🔍 **库搜索**: 通过 `resolve-library-id` 工具搜索并获取 Context7 兼容的库 ID
- 📚 **文档获取**: 通过 `get-library-docs` 工具获取特定库的最新文档
- 🌐 **代理支持**: 支持通过环境变量配置 HTTP/HTTPS 代理
- ⚡ **FastMCP**: 使用 FastMCP 框架，性能优异
- 📦 **单文件实现**: 所有功能集成在一个文件中，部署简单

## 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install httpx pydantic mcp
```

## 使用方法

### 基本运行（stdio 传输）

```bash
python main.py
```

### SSE 传输模式

```bash
python main.py --transport sse --host 0.0.0.0 --port 8088
```

### 配置代理

通过环境变量设置代理，服务器会自动检测和使用代理配置：

```bash
# Windows
set HTTP_PROXY=http://100.108.35.118:12080
set HTTPS_PROXY=http://100.108.35.118:12080
python main.py

# Linux/Mac
export HTTP_PROXY=http://100.108.35.118:12080
export HTTPS_PROXY=http://100.108.35.118:12080
python main.py
```


## MCP 工具

### resolve-library-id

搜索库并获取 Context7 兼容的库 ID。

**参数:**
- `library_name`: 要搜索的库名称

**示例:**
```
resolve-library-id("react")
```

### get-library-docs

获取特定库的文档。

**参数:**
- `context7_compatible_library_id`: Context7 兼容的库 ID
- `topic`: 可选，文档主题
- `tokens`: 可选，最大令牌数量（默认 10000）

**示例:**
```
get-library-docs("/facebook/react", topic="hooks", tokens=15000)
```

## 集成到 MCP 客户端

### Cursor 配置

在 `~/.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "context7-python": {
      "command": "python",
      "args": ["/path/to/python-mcp/main.py"],
      "env": {
        "HTTP_PROXY": "http://100.108.35.118:12080",
        "HTTPS_PROXY": "http://100.108.35.118:12080"
      }
    }
  }
}
```

### Claude Desktop 配置

在配置文件中添加：

```json
{
  "mcpServers": {
    "context7-python": {
      "command": "python",
      "args": ["/path/to/python-mcp/main.py"]
    }
  }
}
```

## 错误处理

- 自动处理速率限制（429 错误）
- 网络错误重试
- 代理连接失败处理
- 详细的错误日志记录

## 技术架构

- **HTTP 客户端**: 使用 `httpx` 进行异步 HTTP 请求
- **数据验证**: 使用 `pydantic` 进行数据模型验证
- **MCP 框架**: 基于 `FastMCP` 构建
- **代理支持**: 自动检测环境变量中的代理配置 