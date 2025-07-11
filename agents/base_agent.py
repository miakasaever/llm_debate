import os
from openai import OpenAI
from typing import  Dict
import time

class BaseAgent:
    """
    BaseAgent实现的是一个抽象类，
    所有的Agent都由Agent继承而来，
    """

    def __init__(self, agent_id: str, role: str, config: Dict):
        self.agent_id = agent_id
        self.role = role
        self.config = config
        
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    
    def llm_api(self, prompt: str, max_retries=3, delay=1) -> str:
        """
        llm大模型API的调用，
        此处我们将温度调成0.1让模型尽可能生成一个相对稳定的内容
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.get("model", "qwen-turbo"),
                    messages=[
                        {"role": "system", "content": "你是一位辩论赛选手"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"API调用失败 ({attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
        return "API调用失败，请检查网络连接和API密钥"

    def generate_response(self, context: Dict) -> str:
        """
        """
        raise NotImplementedError("Subclasses must implement generate_response()")