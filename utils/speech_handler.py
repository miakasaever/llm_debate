import time
import jieba

class SpeechHandler:
    @staticmethod
    def limit_words(text: str, max_words: int = 2000) -> str:
        """
        限制并截断发言长度
        """
        words = jieba.lcut(text)
        if len(words) <= max_words:
            return text
        truncated = ''.join(words[:max_words]) 
        return f"{truncated}（发言已截断，原始长度：{len(words)}字）"
    
    @staticmethod
    def format_response(role: str, content: str, evidences: list) -> dict:
        """
        格式化回复
        """
        return {
            "role": role,
            "content": content,
            "evidences": evidences,
            "timestamp": time.time(),
            "word_count": len(jieba.lcut(content))
        }
    
    @staticmethod
    def validate_speech_length(content: str, max_words: int) -> bool:
        """
        """
        return len(jieba.lcut(content)) <= max_words