# referee_agent.py

from agents.base_agent import BaseAgent
from utils.scoring_system import ScoringSystem


class RefereeAgent(BaseAgent):
    def __init__(self, agent_id: str, role: str, config: dict,llm_use:bool = False):
        super().__init__(agent_id, role, config)
        self.llm_use=llm_use
    
    def generate_response(self, context: dict) -> dict:
        current_speech = context["current_speech"]
        content = current_speech.get("full_content", current_speech.get("content", ""))
        
        scoring_speech = {
            "content": content,
            "role": current_speech.get("role", "辩手"),
            "type": "argument"
        }
        if self.llm_use:
            scores = ScoringSystem.llm_calculate_dimension_scores(
                speech=scoring_speech,
                history=context["speech_history"],
                topic=context["topic"],
                config=self.config
            )
        else:
            scores = ScoringSystem.calculate_dimension_scores(
                speech=scoring_speech,
                history=context["speech_history"],
                topic=context["topic"]
            )

        comment = self._generate_comment(scores)
        
        return {
            "agent_id": self.agent_id,
            "type": "judgment",
            "scores": scores,
            "comment": comment
        }
    
    def _generate_comment(self, scores: dict) -> str:
        comments = []
        
        # logic
        if scores.get("logic", 0) > 0.8:
            comments.append("逻辑严谨有力")
        elif scores.get("logic", 0) < 0.4:
            comments.append("逻辑存在缺陷")
        
        # correlation
        if scores.get("relevance", 0) > 0.8:
            comments.append("与辩题高度相关")
        elif scores.get("relevance", 0) < 0.4:
            comments.append("与辩题相关性不足")
        
        # persuasion
        if scores.get("persuasion", 0) > 0.8:
            comments.append("说服力强")
        elif scores.get("persuasion", 0) < 0.4:
            comments.append("说服力不足")
            
        # defination
        if scores.get("clarity", 0) > 0.8:
            comments.append("表达清晰")
        elif scores.get("clarity", 0) < 0.4:
            comments.append("表达不够清晰")
            
        # profundity
        if scores.get("depth", 0) > 0.8:
            comments.append("论证深入")
        elif scores.get("depth", 0) < 0.4:
            comments.append("论证深度不足")
        
        return "；".join(comments) if comments else "表现均衡"


