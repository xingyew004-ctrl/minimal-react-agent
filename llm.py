import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class HelloAgentsLLM:
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = (base_url or os.getenv("LLM_BASE_URL") or "").rstrip("/")
        self.timeout = int(timeout or os.getenv("LLM_TIMEOUT", 60))

        if not self.model:
            raise ValueError("缺少 LLM_MODEL_ID")
        if not self.api_key:
            raise ValueError("缺少 LLM_API_KEY")
        if not self.base_url:
            raise ValueError("缺少 LLM_BASE_URL")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> Optional[str]:
        print(f"--- 调用 LLM ---")
        print(f"🧠 正在调用模型: {self.model}")
        print(f"🌐 服务地址: {self.base_url}")

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            print("✅ 大语言模型响应成功:")
            collected_content = []

            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                content = delta.content or ""
                if content:
                    print(content, end="", flush=True)
                    collected_content.append(content)

            print()
            return "".join(collected_content)

        except Exception as e:
            error_text = str(e)
            print(f"\n❌ 调用 LLM API 时发生错误: {error_text}")

            if "insufficient_quota" in error_text:
                print("👉 诊断结果：当前不是代码问题，而是账号额度不足或计费/配额未开通。")
            elif "401" in error_text or "authentication" in error_text.lower():
                print("👉 诊断结果：API Key 无效，或者认证失败。")
            elif "404" in error_text or "model" in error_text.lower():
                print("👉 诊断结果：模型名可能不对，或者该模型不可用。")
            elif "429" in error_text:
                print("👉 诊断结果：请求被限流，或者配额不足。")
            else:
                print("👉 诊断结果：请检查 base_url、model_id、网络环境和服务端状态。")

            return None


if __name__ == "__main__":
    llm_client = HelloAgentsLLM()

    example_messages = [
        {"role": "system", "content": "You are a helpful assistant that writes Python code."},
        {"role": "user", "content": "写一个快速排序算法"},
    ]

    response = llm_client.think(example_messages)

    if response:
        print("\n\n--- 完整模型响应 ---")
        print(response)