#---------------------------------------------------------
# knowledge_validator.py
# This is a program designed to verify the logical structure of arguments
#---------------------------------------------------------

class KnowledgeValidator:
    @staticmethod
    def validate_format(response: dict) -> dict:
        """
        用来验证发言内容的格式
        :param response: a dict
        :return: valid dict
        """
        required_keys = {"argument", "evidence"}
        if not all(key in response for key in required_keys):
            raise ValueError("响应缺少必要字段，必须包含 'argument' 和 'evidence'")
        
        if not isinstance(response['argument'], str):
            raise TypeError("'argument' 必须是字符串类型")
        
        if not isinstance(response['evidence'], list) or \
           not all(isinstance(item, str) for item in response['evidence']):
            raise TypeError("'evidence' 必须是字符串列表")
        
        return {
            "argument": response["argument"].strip(),
            "evidence": [evid.strip() for evid in response["evidence"]]
        }