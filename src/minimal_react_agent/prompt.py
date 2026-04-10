from typing import Dict, List


REACT_SYSTEM_PROMPT = """你是一个能够调用外部工具来解决问题的智能助手。

你可以使用的工具如下：
{tools}

你的任务目标：
- 围绕用户原始问题作答，不要擅自改变问题定义。
- 只有在现有信息不足时才调用工具。
- 一旦已有信息足以回答问题，必须立即使用 Finish[最终答案] 结束。

你必须严格遵守以下输出格式：
Thought: 说明你对当前问题的判断，以及为什么要采取下一步行动。
Action: 你的行动

其中，Action 只能是以下两种形式之一：
1. 工具调用：工具名[工具输入]
2. 结束回答：Finish[最终答案]

严格规则：
- 必须先输出 Thought，再输出 Action。
- 不要输出 Observation；Observation 由系统在工具执行后提供给你。
- 不要输出多余解释、客套话、前后缀说明。
- 不要输出 Markdown 代码块。
- 必须使用半角中括号 []。
- 工具名必须与工具列表中的名称完全一致，不能编造工具。
- 如果上一步 Observation 已经足够回答问题，就不要继续调用工具。
- 不要重复调用与上一步相同的工具和相同意图的查询，除非你能明确说明新的查询目标。
- 若搜索结果存在多个维度（例如消费级、企业级、时间线不同），只有在确有必要时才补充区分，并明确说明这是补充说明，不要替换原问题。
"""


def format_history(intermediate_steps: List[Dict[str, str]]) -> str:
    """
    将中间步骤格式化成 History 文本。
    每个 step 期望至少包含:
    {
        "thought": "...",
        "action": "...",
        "observation": "..."
    }
    """
    if not intermediate_steps:
        return "无"

    history_blocks = []
    for idx, step in enumerate(intermediate_steps, start=1):
        thought = step.get("thought", "").strip() or "(无)"
        action = step.get("action", "").strip() or "(无)"
        observation = step.get("observation", "").strip() or "(无)"

        block = (
            f"Step {idx}\n"
            f"Thought: {thought}\n"
            f"Action: {action}\n"
            f"Observation: {observation}"
        )
        history_blocks.append(block)

    return "\n\n".join(history_blocks)


def build_react_messages(
    question: str,
    tools_text: str,
    intermediate_steps: List[Dict[str, str]],
):
    question = (question or "").strip()
    tools_text = (tools_text or "").strip()
    history_text = format_history(intermediate_steps)

    system_prompt = REACT_SYSTEM_PROMPT.format(tools=tools_text)

    user_prompt = f"""请基于以下信息继续解决问题。

用户原始问题：
{question}

历史记录：
{history_text}

请注意：
- 你当前只能输出 Thought 和 Action。
- 如果历史记录中的 Observation 已经足够回答问题，请直接输出 Finish[最终答案]。
- 最终答案应直接回应“用户原始问题”，不要偏离。
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]