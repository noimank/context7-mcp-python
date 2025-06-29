#!/usr/bin/env python3
"""
Context7 MCP Server - Python Implementation
Up-to-date Code Docs For Any Prompt

This MCP server provides up-to-date documentation and code examples
for libraries by interfacing with Context7 API.
"""

# __version__ = "1.0.1"

import argparse
import asyncio
import os
from typing import Optional, List

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# 常量配置
CONTEXT7_API_BASE_URL = "https://context7.com/api"
DEFAULT_TYPE = "txt"
DEFAULT_MINIMUM_TOKENS = 10000

# 解析命令行参数
parser = argparse.ArgumentParser(description="Context7 MCP Server")
parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                    help="传输类型 (默认: stdio)")
parser.add_argument("--port", type=int, default=34504,
                    help="sse服务器端口 (默认: 34504)")
parser.add_argument("--host", type=str, default="localhost",
                    help="sse服务地址 (默认：localhost)")

args, unknown = parser.parse_known_args()


# 数据模型
class SearchResult(BaseModel):
    id: str
    title: str
    description: str
    branch: str
    lastUpdateDate: str
    state: str
    totalTokens: int
    totalSnippets: int
    totalPages: int
    stars: Optional[int] = None
    trustScore: Optional[float] = None  # 修改为float类型以支持小数
    versions: Optional[List[str]] = None


class SearchResponse(BaseModel):
    error: Optional[str] = None
    results: List[SearchResult] = Field(default_factory=list)


# HTTP客户端配置
def get_http_client() -> httpx.AsyncClient:
    """创建HTTP客户端，显式支持代理配置"""
    # 从环境变量获取代理配置
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')

    # 显示代理配置状态
    if http_proxy:
        print(f"✓ 检测到HTTP代理: {http_proxy}")
    if https_proxy:
        print(f"✓ 检测到HTTPS代理: {https_proxy}")

    if not http_proxy and not https_proxy:
        print("ℹ 未配置代理，使用直连")

    # 尝试多种代理配置方式以确保兼容性
    client = None

    # 方式1: 尝试使用proxies参数 (httpx >= 0.23.0)
    if (http_proxy or https_proxy) and client is None:
        try:
            proxy_dict = {}
            if http_proxy:
                proxy_dict['http://'] = http_proxy
            if https_proxy:
                proxy_dict['https://'] = https_proxy

            client = httpx.AsyncClient(
                proxies=proxy_dict,
                timeout=httpx.Timeout(30.0),
                headers={'User-Agent': 'Context7-MCP-Python/1.0.0'}
            )
            print("✓ 使用proxies参数配置代理成功")
        except (TypeError, ValueError) as e:
            print(f"⚠ proxies参数不支持: {e}")
            client = None

    # 方式2: 尝试使用单个proxy参数
    if (http_proxy or https_proxy) and client is None:
        try:
            # 优先使用HTTPS代理，如果没有则使用HTTP代理
            proxy_url = https_proxy or http_proxy
            client = httpx.AsyncClient(
                proxy=proxy_url,
                timeout=httpx.Timeout(30.0),
                headers={'User-Agent': 'Context7-MCP-Python/1.0.0'}
            )
            print(f"✓ 使用单一代理配置成功: {proxy_url}")
        except (TypeError, ValueError) as e:
            print(f"⚠ proxy参数不支持: {e}")
            client = None

    # 方式3: 回退到环境变量方式（httpx自动读取）
    if client is None:
        try:
            client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={'User-Agent': 'Context7-MCP-Python/1.0.0'}
            )
            if http_proxy or https_proxy:
                print("✓ 使用环境变量代理配置（httpx自动检测）")
            else:
                print("✓ 创建直连客户端")
        except Exception as e:
            print(f"✗ 创建HTTP客户端失败: {e}")
            raise

    return client


# API函数
async def search_libraries(query: str) -> SearchResponse:
    """
    搜索匹配给定查询的库

    Args:
        query: 搜索查询字符串

    Returns:
        搜索结果或错误信息
    """
    try:
        client = get_http_client()
        url = f"{CONTEXT7_API_BASE_URL}/v1/search"
        params = {"query": query}

        async with client:
            response = await client.get(url, params=params)

            if response.status_code == 429:
                error_msg = "由于请求过多导致频率限制。请稍后再试。"
                print(f"错误: {error_msg}")
                return SearchResponse(results=[], error=error_msg)

            if not response.is_success:
                error_msg = f"搜索库失败。请稍后再试。错误代码: {response.status_code}"
                print(f"错误: {error_msg}")
                return SearchResponse(results=[], error=error_msg)

            data = response.json()
            return SearchResponse(**data)

    except Exception as error:
        error_msg = f"搜索库时出错: {error}"
        print(f"错误: {error_msg}")
        return SearchResponse(results=[], error=error_msg)


async def fetch_library_documentation(
        library_id: str,
        tokens: Optional[int] = None,
        topic: Optional[str] = None
) -> Optional[str]:
    """
    获取特定库的文档上下文

    Args:
        library_id: 要获取文档的库ID
        tokens: 令牌数量限制
        topic: 主题筛选

    Returns:
        文档文本或None（请求失败时）
    """
    try:
        # 处理库ID格式
        if library_id.startswith("/"):
            library_id = library_id[1:]

        client = get_http_client()
        url = f"{CONTEXT7_API_BASE_URL}/v1/{library_id}"

        params = {"type": DEFAULT_TYPE}
        if tokens:
            params["tokens"] = str(tokens)
        if topic:
            params["topic"] = topic

        headers = {"X-Context7-Source": "mcp-server-python"}

        async with client:
            response = await client.get(url, params=params, headers=headers)

            if response.status_code == 429:
                error_msg = "由于请求过多导致频率限制。请稍后再试。"
                print(f"错误: {error_msg}")
                return error_msg

            if not response.is_success:
                error_msg = f"获取文档失败。请稍后再试。错误代码: {response.status_code}"
                print(f"错误: {error_msg}")
                return error_msg

            text = response.text
            if not text or text in ["No content available", "No context data available"]:
                return None

            return text

    except Exception as error:
        error_msg = f"获取库文档时出错。请稍后再试。{error}"
        print(f"错误: {error_msg}")
        return error_msg


# 辅助函数
def format_search_result(result: SearchResult) -> str:
    """
    将搜索结果格式化为人类可读的字符串表示
    只在可用时显示代码片段数量和GitHub星数（不等于-1）
    """
    # 始终包含这些基本详细信息
    formatted_result = [
        f"- 标题: {result.title}",
        f"- Context7兼容库ID: {result.id}",
        f"- 描述: {result.description}",
    ]

    # 只有在有效值时才添加代码片段数量
    if result.totalSnippets != -1 and result.totalSnippets is not None:
        formatted_result.append(f"- 代码片段: {result.totalSnippets}")

    # 只有在有效值时才添加信任分数
    if result.trustScore != -1 and result.trustScore is not None:
        formatted_result.append(f"- 信任分数: {result.trustScore:.1f}")

    # 只有在有效值时才添加版本
    if result.versions is not None and len(result.versions) > 0:
        formatted_result.append(f"- 版本: {', '.join(result.versions)}")

    # 用换行符连接所有部分
    return "\n".join(formatted_result)


def format_search_results(search_response: SearchResponse) -> str:
    """
    将搜索响应格式化为人类可读的字符串表示
    每个结果使用format_search_result进行格式化
    """
    if not search_response.results or len(search_response.results) == 0:
        return "未找到匹配您查询的文档库。"

    formatted_results = [format_search_result(result) for result in search_response.results]
    return "\n----------\n".join(formatted_results)


# 创建FastMCP应用
mcp = FastMCP("Context7", host="0.0.0.0", port=args.port, instructions="使用此服务器检索任何库的最新文档和代码示例。")


@mcp.tool()
async def resolve_library_id(library_name: str) -> str:
    """
    将包/产品名称解析为Context7兼容的库ID，并返回匹配库的列表。

    在调用'get-library-docs'之前，您必须调用此函数以获取有效的Context7兼容库ID，
    除非用户在其查询中明确提供了'/org/project'或'/org/project/version'格式的库ID。

    选择过程：
    1. 分析查询以了解用户正在寻找什么库/包
    2. 根据以下条件返回最相关的匹配：
    - 与查询的名称相似性（优先完全匹配）
    - 描述与查询意图的相关性
    - 文档覆盖范围（优先代码片段数量较高的库）
    - 信任分数（考虑分数为7-10的库更权威）

    响应格式：
    - 在明确标记的部分中返回选定的库ID
    - 提供选择此库的简要说明
    - 如果存在多个好的匹配，请承认这一点，但继续使用最相关的一个
    - 如果没有好的匹配，请明确说明并建议查询优化

    对于模糊查询，请在继续最佳猜测匹配之前请求澄清。

    参数：
        library_name: 要搜索并检索Context7兼容库ID的库英文名称，不要传入中文，不要传入版本号，不要传入任何其他信息。

    返回：
        格式化的搜索结果字符串
    """
    search_response = await search_libraries(library_name)

    if not search_response.results or len(search_response.results) == 0:
        return (search_response.error if search_response.error
                else "无法从Context7检索库文档数据")

    results_text = format_search_results(search_response)

    return f"""可用库（热门匹配）:

每个结果包括：
- 库ID: Context7兼容标识符（格式: /org/project）
- 名称: 库或包名称
- 描述: 简短摘要
- 代码片段: 可用代码示例数量
- 信任分数: 权威性指标
- 版本: 版本列表（如果可用）。当且仅当用户在其查询中明确提供版本时，使用其中一个版本。

为获得最佳结果，请根据名称匹配、信任分数、片段覆盖范围和与您用例的相关性选择库。

----------

{results_text}"""


@mcp.tool()
async def get_library_docs(
        context7_compatible_library_id: str,
        topic: str = "",
        tokens: int = DEFAULT_MINIMUM_TOKENS
) -> str:
    """
    获取库的最新文档。您必须首先调用'resolve-library-id'以获取使用此工具所需的确切Context7兼容库ID，
    除非用户在其查询中明确提供了'/org/project'或'/org/project/version'格式的库ID。

    参数：
        context7_compatible_library_id: 确切的Context7兼容库ID（例如，'/mongodb/docs'、'/vercel/next.js'、
            '/supabase/supabase'、'/vercel/next.js/v14.3.0-canary.87'），从'resolve-library-id'检索或
            直接从用户查询中获取，格式为'/org/project'或'/org/project/version'。
        topic: 文档关注的主题（例如，'hooks'、'routing'）。
        tokens: 要检索的文档的最大令牌数量（默认: 10000）。更高的值提供更多上下文但消耗更多令牌。

    返回：
        文档内容或错误消息
    """
    # 确保tokens不小于默认最小值
    if tokens < DEFAULT_MINIMUM_TOKENS:
        tokens = DEFAULT_MINIMUM_TOKENS

    fetch_docs_response = await fetch_library_documentation(
        context7_compatible_library_id,
        tokens=tokens,
        topic=topic
    )

    if not fetch_docs_response:
        return ("未找到此库的文档或文档未完成。这可能是因为您使用了无效的Context7兼容库ID。"
                "要获取有效的Context7兼容库ID，请使用您希望检索文档的包名称调用'resolve-library-id'。")

    return fetch_docs_response


async def test_proxy_connection():
    """测试代理连接是否正常"""
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')

    if not http_proxy and not https_proxy:
        print("ℹ 未配置代理，跳过代理测试")
        return True

    print("\n🔍 测试代理连接...")
    try:
        client = get_http_client()
        async with client:
            # 测试HTTP连接
            response = await client.get("http://httpbin.org/ip", timeout=10.0)
            if response.status_code == 200:
                ip_info = response.json()
                print(f"✓ 代理连接成功，出口IP: {ip_info.get('origin', 'unknown')}")
                return True
            else:
                print(f"⚠ 代理测试失败，状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"⚠ 代理连接测试失败: {e}")
        print("ℹ 将继续使用配置的代理，请确保代理服务器正常运行")
        return False


def main():
    """主函数 - 启动MCP服务器"""
    print("Context7 MCP 服务器 - Python 版本")
    print("==================================")

    # 测试代理连接
    if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_proxy_connection())
            loop.close()
        except Exception as e:
            print(f"⚠ 代理测试异常: {e}")

    print(f"\n🚀 启动MCP服务器 (传输方式: {args.transport})")

    # 启动服务器
    if args.transport == "sse":
        print("sse服务地址为： http://" + args.host + ":" + str(args.port) + "/sse")
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
