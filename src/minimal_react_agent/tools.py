import os
from dataclasses import dataclass
from typing import Callable, Dict, Any
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


def _pick_first_text(*values):
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _format_answer_box(answer_box: Dict[str, Any]):
    if not isinstance(answer_box, dict):
        return None

    highlighted = answer_box.get("snippet_highlighted_words")
    highlighted_text = None
    if isinstance(highlighted, list) and highlighted:
        highlighted_text = str(highlighted[0]).strip()

    title = answer_box.get("title")
    text = _pick_first_text(
        answer_box.get("answer"),
        answer_box.get("snippet"),
        highlighted_text,
    )

    if not text:
        return None

    if title and title not in text:
        return f"{title}\n{text}"
    return text


def search(query: str) -> str:
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")

    api_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY")
    if not api_key:
        return "错误：未找到 SERPAPI_API_KEY（或 SERPAPI_KEY），请检查 .env 配置。"

    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",
            "hl": "zh-cn",
            "google_domain": "google.com",
            "num": 5,
        }

        search_client = GoogleSearch(params)
        results = search_client.get_dict()

        answer_box = results.get("answer_box")
        parsed_answer = _format_answer_box(answer_box)
        if parsed_answer:
            return parsed_answer

        knowledge_graph = results.get("knowledge_graph", {})
        if isinstance(knowledge_graph, dict):
            kg_title = knowledge_graph.get("title")
            kg_desc = _pick_first_text(
                knowledge_graph.get("description"),
                knowledge_graph.get("snippet"),
            )
            if kg_desc:
                return f"{kg_title}\n{kg_desc}" if kg_title else kg_desc

        organic_results = results.get("organic_results", [])
        if isinstance(organic_results, list) and organic_results:
            snippets = []
            for i, res in enumerate(organic_results[:3], start=1):
                title = res.get("title", "无标题")
                snippet = _pick_first_text(res.get("snippet")) or "无摘要"
                link = res.get("link", "")

                block = f"[{i}] {title}\n{snippet}"
                if link:
                    block += f"\n{link}"
                snippets.append(block)

            return "\n\n".join(snippets)

        return f"对不起，没有找到关于「{query}」的有效信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[[str], str]


class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        if tool.name in self.tools:
            raise ValueError(f"工具 {tool.name} 已存在，不能重复注册。")
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        if name not in self.tools:
            raise ValueError(f"工具 {name} 不存在。")
        return self.tools[name]

    def call_tool(self, name: str, tool_input: str) -> str:
        tool = self.get_tool(name)
        return tool.func(tool_input)

    def get_tool_descriptions(self) -> str:
        return "\n".join(
            f"{tool.name}: {tool.description}"
            for tool in self.tools.values()
        )


if __name__ == "__main__":
    print("tools.py 开始执行")

    manager = ToolManager()

    manager.register_tool(
        Tool(
            name="Search",
            description=(
                "当你需要查询最新信息、网页事实、人物资料、新闻、"
                "外部知识或无法仅靠已有知识回答的问题时，使用这个工具。"
                "输入应为一个清晰的搜索问题。"
            ),
            func=search,
        )
    )

    print("=== 当前可用工具 ===")
    print(manager.get_tool_descriptions())

    print("\n=== 测试调用 Search ===")
    result = manager.call_tool("Search", "英伟达最新的GPU型号是什么")
    print(result)