from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from minimal_react_agent.agent import ReActAgent
from minimal_react_agent.llm import HelloAgentsLLM
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

    agent = ReActAgent(
        llm_client=llm,
        tool_manager=manager,
        max_steps=5,
    )

    question = "英伟达最新的 GPU 型号是什么？"
    answer = agent.run(question)

    print("\n=== Final Answer ===")
    print(answer)


if __name__ == "__main__":
    main()
