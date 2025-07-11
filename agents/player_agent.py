from agents.base_agent import BaseAgent
from typing import Dict


class PlayerAgent(BaseAgent):
    def __init__(self, agent_id: str, role: str, config: Dict):
        super().__init__(agent_id, role, config)

    def generate_response(self, context: dict) -> dict:
        print("\n" + "=" * 50)
        print(f"【当前辩题】: {context['topic']}")
        print(f"【你的角色】: {self.role}方辩手")

        history = context.get("speech_history", [])
        if history:
            print("\n【历史发言摘要】:")
            for i, speech in enumerate(history[-3:]):
                role = speech.get('role', '辩手')
                content = speech.get('content', '')[:80] + "..." if len(speech.get('content', '')) > 80 else speech.get(
                    'content', '')
                print(f"{i + 1}. {role}: {content}")

        print("\n" + "=" * 50)
        argument = input("请输入你的论点: ")
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "type": "argument",
            "content": argument,
            "evidence": []
        }
