# Context7 MCP Python Server

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.3-orange.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)

**🚀  Context7 MCP Python版本服务器实现 - 为您的 AI 助手提供最新的代码文档**

[功能特点](#-功能特点) • [快速开始](#-快速开始) • [安装指南](#-安装指南) • [使用文档](#-使用文档) • [配置说明](#️-配置说明) • [贡献指南](#-贡献指南)

</div>

---

## 📋 项目概述

Context7 MCP Python Server 是一个高性能的 Model Context Protocol (MCP) 服务器实现，专为 AI 助手提供实时、准确的代码库文档和示例。通过与 Context7 API 的深度集成，为开发者提供最新的库文档、代码片段和最佳实践。

### 🎯 核心价值

- **🔄 实时更新**: 获取最新的库文档和代码示例
- **🎯 智能搜索**: 精准匹配您需要的技术文档
- **⚡ 高性能**: 基于 FastMCP 框架，响应迅速
- **🌐 代理友好**: 完善的网络代理支持
- **🔧 易于集成**: 无缝集成到各种 MCP 客户端

## ✨ 功能特点

### 🔍 智能库搜索
- **精准匹配**: 通过 `resolve-library-id` 工具快速定位目标库
- **多维度搜索**: 支持库名、描述、标签等多种搜索方式
- **实时结果**: 获取库的最新状态、版本信息和可信度评分

### 📚 文档获取服务
- **按需获取**: 通过 `get-library-docs` 工具获取特定库的详细文档
- **主题筛选**: 支持按主题获取相关文档片段
- **令牌控制**: 灵活控制返回内容的长度和详细程度

### 🌐 网络连接优化
- **多重代理支持**: 自动检测和配置 HTTP/HTTPS 代理
- **连接重试**: 智能重试机制，确保服务稳定性
- **错误处理**: 完善的错误处理和日志记录

### 🏗️ 架构优势
- **异步处理**: 基于 asyncio 的高并发处理能力
- **类型安全**: 使用 Pydantic 进行数据验证和类型检查
- **模块化设计**: 清晰的代码结构，易于维护和扩展

## 🚀 快速开始

### 前置需求
- Python 3.8 或更高版本
- pip 包管理器

### 一键安装
```bash
pip install context7-mcp-python
```

### 基础使用
```bash
# 启动服务器（stdio 模式）
context7-mcp-python

# 启动 SSE 服务器
context7-mcp-python --transport sse --host 0.0.0.0 --port 8088
```

## 📦 安装指南

### 方式一：从 PyPI 安装（推荐）
```bash
pip install context7-mcp-python
```

### 方式二：从源码安装
```bash
git clone https://github.com/noimank/context7-mcp-python.git
cd context7-mcp-python
pip install -r requirements.txt
```



## 📖 使用文档

### MCP 工具说明

#### 🔍 `resolve-library-id`
搜索并获取 Context7 兼容的库 ID

**参数:**
- `library_name` (string): 要搜索的库名称

**示例:**
```python
# 搜索 React 库
resolve_library_id("react")

# 搜索 FastAPI 库
resolve_library_id("fastapi")
```

**返回格式:**
```
📚 找到 3 个匹配的库:

🔹 facebook/react
   📋 描述: A declarative, efficient, and flexible JavaScript library
   ⭐ Stars: 220000 | 🎯 信任度: 0.95 | 📊 令牌数: 850000
   📅 最后更新: 2024-01-15 | 🏷️ 状态: active

🔹 react-native-community/react-native
   📋 描述: A framework for building native apps using React
   ⭐ Stars: 115000 | 🎯 信任度: 0.88 | 📊 令牌数: 420000
   📅 最后更新: 2024-01-14 | 🏷️ 状态: active
```

#### 📚 `get-library-docs`
获取特定库的详细文档

**参数:**
- `context7_compatible_library_id` (string): Context7 兼容的库 ID
- `topic` (string, 可选): 文档主题筛选
- `tokens` (integer, 可选): 最大令牌数量，默认 10000

**示例:**
```python
# 获取 React 基础文档
get_library_docs("/facebook/react")

# 获取 React Hooks 相关文档
get_library_docs("/facebook/react", topic="hooks", tokens=15000)

# 获取 FastAPI 认证相关文档
get_library_docs("/tiangolo/fastapi", topic="authentication")
```

### 命令行选项

```bash
context7-mcp-python [选项]

选项:
  --transport {stdio,sse}  传输协议类型 (默认: stdio)
  --port PORT             SSE 服务器端口 (默认: 34504)
  --host HOST             SSE 服务器地址 (默认: localhost)
  -h, --help              显示帮助信息
```

## ⚙️ 配置说明

### 环境变量配置

#### 代理设置
设置 HTTP 和 HTTPS 的代理环境变量，contex7-mcp-python会自动读取使用。

```bash
# Windows
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080

# Linux/macOS
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### MCP 客户端集成

#### Cursor 等IDE 配置
在 `~/.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "context7-python": {
      "command": "uvx",
      "args":[
        "context7-mcp-python"
      ]
      "env": {
        "HTTP_PROXY": "http://proxy.example.com:8080",
        "HTTPS_PROXY": "http://proxy.example.com:8080"
      }
    }
  }
}
```


## 🛠️ 故障排除

### 常见问题

#### 1. 网络连接问题
```bash
# 检查代理配置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 测试网络连接
curl -I https://context7.com/api/v1/search
```

#### 2. 权限问题
```bash
# 确保有足够的权限
chmod +x server.py

# 检查 Python 版本
python --version
```

#### 3. 依赖冲突
```bash
# 重新安装依赖
pip uninstall context7-mcp-python
pip install context7-mcp-python

# 或使用虚拟环境
python -m venv fresh_env
source fresh_env/bin/activate
pip install context7-mcp-python
```



## 🤝 贡献指南

欢迎所有形式的贡献！

### 贡献方式
1. 🐛 报告 Bug
2. 💡 提出新功能建议
3. 📝 改进文档
4. 🔧 提交代码修复

### 提交流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的测试用例
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Context7](https://context7.com) - 提供强大的 API 服务
- [FastMCP](https://github.com/jlowin/fastmcp) - 优秀的 MCP 框架
- [httpx](https://www.python-httpx.org/) - 现代的 HTTP 客户端
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库

## 📞 联系我

- 📧 Email: noimank@163.com
- 🐛 Issues: [GitHub Issues](https://github.com/noimank/context7-mcp-python/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/noimank/context7-mcp-python/discussions)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给项目一个 Star！**

Made with ❤️ by [noimank](https://github.com/noimank)

</div> 