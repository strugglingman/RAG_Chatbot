import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.config.settings import Config


async def search_with_mcp(query: str) -> str:
    """Search using MCP server when local docs don't have answer"""
    try:
        server_params = StdioServerParameters(
            command=Config.MCP_SERVER_COMMAND.split()[0],
            args=Config.MCP_SERVER_COMMAND.split()[1:],
            env=None,
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("brave_search", {"query": query})
                return result.content[0].text
    except Exception as e:
        return f"Error during MCP search: {str(e)}"


def search_external(query: str) -> str:
    """Sync wrapper for MCP search"""
    return asyncio.run(search_with_mcp(query))
