from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from minimal_react_agent.llm import HelloAgentsLLM
from minimal_react_agent.prompt import build_react_messages
from minimal_react_agent.tools import Tool, ToolManager, search


def main() -> None:
    llm = HelloAgentsLLM()

    manager = ToolManager()
    manager.register_tool(
        Tool(
            name="Search",
            description="Use this tool when you need web facts or recent external information.",
            func=search,
        )
    )

    question = "英伟达最新的 GPU 型号是什么？"
    intermediate_steps = []

    messages = build_react_messages(
        question=question,
        tools_text=manager.get_tool_descriptions(),
        intermediate_steps=intermediate_steps,
    )

    print("=== Messages Sent To LLM ===")
    for msg in messages:
        print(f"\n[{msg['role']}]\n{msg['content']}")

    print("\n=== LLM Output ===")
    response = llm.think(messages)
    print("\n\n=== Raw Response ===")
    print(response)


if __name__ == "__main__":
    main()
