import re
from typing import Dict, List, Optional, Tuple

from .llm import HelloAgentsLLM
from .prompt import build_react_messages
from .tools import ToolManager


class ReActAgent:
    def __init__(
        self,
        llm_client: HelloAgentsLLM,
        tool_manager: ToolManager,
        max_steps: int = 5,
        max_observation_chars: int = 800,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than 0")
        if max_observation_chars <= 0:
            raise ValueError("max_observation_chars must be greater than 0")

        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.max_steps = max_steps
        self.max_observation_chars = max_observation_chars
        self.history: List[Dict[str, str]] = []

    def _strip_code_fence(self, text: str) -> str:
        text = text.strip()
        fenced_match = re.fullmatch(r"```[a-zA-Z0-9_-]*\n?(.*?)\n?```", text, re.DOTALL)
        if fenced_match:
            return fenced_match.group(1).strip()
        return text

    def _normalize_action_text(self, action_text: str) -> str:
        action_text = action_text.strip().strip("`").strip()
        return re.sub(r"\s+", " ", action_text)

    def _truncate_observation(self, text: str) -> str:
        text = (text or "").strip()
        if len(text) <= self.max_observation_chars:
            return text
        return text[: self.max_observation_chars] + "\n...(truncated)"

    def _is_repeated_action(self, action_text: str) -> bool:
        if not self.history:
            return False
        last_action = self.history[-1].get("action", "")
        return self._normalize_action_text(last_action) == self._normalize_action_text(action_text)

    def _parse_response(self, response_text: str) -> Optional[Tuple[str, str]]:
        if not response_text:
            return None

        text = self._strip_code_fence(response_text)
        thought_match = re.search(
            r"^\s*Thought[:：]\s*(.*?)(?=^\s*Action[:：]|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        action_match = re.search(
            r"^\s*Action[:：]\s*(.*)$",
            text,
            re.MULTILINE | re.DOTALL,
        )

        if not thought_match or not action_match:
            return None

        thought = thought_match.group(1).strip()
        action = action_match.group(1).strip()
        action = re.sub(r"^[-*]\s*", "", action).strip()
        action = action.strip("`").strip()

        if not thought or not action:
            return None
        return thought, action

    def _parse_action(self, action_text: str) -> Tuple[str, str]:
        cleaned = action_text.strip().strip("`").strip()

        finish_match = re.fullmatch(r"Finish\s*\[(.*)\]\s*", cleaned, re.DOTALL)
        if finish_match:
            return "finish", finish_match.group(1).strip()

        tool_match = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*)\]\s*",
            cleaned,
            re.DOTALL,
        )
        if tool_match:
            return tool_match.group(1).strip(), tool_match.group(2).strip()

        raise ValueError(f"Cannot parse Action format: {action_text}")

    def run(self, question: str) -> str:
        question = (question or "").strip()
        if not question:
            return "Error: question cannot be empty."

        self.history = []
        tools_desc = self.tool_manager.get_tool_descriptions().strip()
        if not tools_desc:
            return "Error: no tools are registered."

        for step in range(1, self.max_steps + 1):
            print(f"\n--- Step {step} ---")

            messages = build_react_messages(
                question=question,
                tools_text=tools_desc,
                intermediate_steps=self.history,
            )
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                return "Error: LLM did not return a valid response."

            parsed = self._parse_response(response_text)
            if not parsed:
                return f"Error: cannot parse LLM output.\nRaw output:\n{response_text}"

            thought, action_text = parsed
            print("\n[Parsed]")
            print(f"Thought: {thought}")
            print(f"Action: {action_text}")

            try:
                action_name, action_payload = self._parse_action(action_text)
            except ValueError as exc:
                return f"Error: {exc}\nRaw output:\n{response_text}"

            if action_name == "finish":
                print("\nTask completed.")
                return action_payload

            if self._is_repeated_action(action_text):
                return f"Error: repeated action detected: {action_text}"

            try:
                observation = self.tool_manager.call_tool(action_name, action_payload)
            except Exception as exc:
                observation = f"Tool execution failed: {exc}"

            observation = self._truncate_observation(observation)
            print(f"\nObservation: {observation}")

            self.history.append(
                {
                    "thought": thought,
                    "action": action_text,
                    "observation": observation,
                }
            )

        return f"Error: reached max steps ({self.max_steps}) without finishing."
