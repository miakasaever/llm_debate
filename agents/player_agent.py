from agents.base_agent import BaseAgent
from typing import Dict


class PlayerAgent(BaseAgent):
    def __init__(self, agent_id: str, role: str, config: Dict):
        super().__init__(agent_id, role, config)

    def generate_response(self, context: dict) -> dict:
        print("\n" + "=" * 50)
        print(f"【当前辩题】: {context['topic']}")
        print(f"【你的角色】: {self.role}")
        print("\n" + "=" * 50)
        argument = input("请输入你的论点: ")
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "type": "argument",
            "content": argument,
            "evidence": []
        }
