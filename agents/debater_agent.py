# debater_agent.py

from agents.base_agent import BaseAgent
from utils.speech_handler import SpeechHandler

class DebaterAgent(BaseAgent):
    def __init__(self, agent_id: str, role: str, config: dict):
        super().__init__(agent_id, role, config)
        self.max_words = config.get("max_speech_length", 1000)

    def generate_response(self, context: dict) -> dict:
        original_argument = self._generate_claim(context)
        truncated_content = SpeechHandler.limit_words(original_argument, self.max_words)
        
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "type" : "argument",
            "full_content": original_argument,  
            "content": truncated_content,   
        }

    def _generate_claim(self, context: dict) -> str:
        '''
        '''
        history_summary = self._summarize_history(context.get("speech_history", []))
        
        prompt = f"""
    你作为{self.role}方辩手，当前辩题：{context['topic']}。\n
    
    ### 以下是其他辩手的历史发言记录\n
    {history_summary}\n
    
    ### 你的任务：
    你需要按以下步骤一步一步思考并给出你的发言\n
    1.首先，你需要分析并总结同为{self.role}方辩手的发言，并依照其中的论点逻辑组织更加强力的论证语言。\n
    2.然后，你需要分析另一方对手的发言。你需要一步步思考对方论证过程中的逻辑漏洞和思维缺陷，并从让己方更容易获胜的角度攻击对方的逻辑缺陷。\n
    3.最后，你可以选择使用一些更加生活化，通俗化的例子来解释你的例证，并鼓动观众的情绪。\n
    
    ###请一步步仔细思考，最终你的发言将包含\n
    1.首先,你的发言必须组织成一个辩手的语言，自然而且通畅\n
    2.同时，你的论证在条件允许的情况下需要有完整的逻辑链条（除了常识性的知识不用再次说明）\n
    3.注意，如果是立论阶段，你的重点放在建构起己方的观点上；质询阶段的重点在于反驳对方的结论；结辩环节的重点在于总结己方的结论，并对对方的结论进行最后一次反攻\n
    4.最后，你的发言内容大致遵从 驳斥对方观点-保护己方观点-煽动观众情绪\n
    
    
    ###再次强调，你是一位辩手，不要机械式地陈列观点，而是组织成自然的语言表述出来，不要简单陈列观点！！！\n
    ###你的内容只需要包含你发言稿的部分！不需要再加入你分析的过程！！！
        """
        try:
            response = self.llm_api(prompt,self.config)
            return response.strip()
        except Exception as e:
            print(f"论点生成失败: {str(e)}")
            return "论点生成失败"
    
    def _summarize_history(self, history: list) -> str:
        """
        综合发言历史
        """
        if not history:
            return "暂无历史发言"
            
        return "\n".join(
            f"{idx+1}. {item.get('role', '辩手')}: {item.get('content', '')[:80]}"
            for idx, item in enumerate(history[-3:])
        )