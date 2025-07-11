# scoring_system.py
import time
import jieba 
from typing import List, Dict
from openai import OpenAI
import os
import re
import json


def llm_api(prompt: str, max_retries=3, delay=1) -> str:
    """
    llm大模型API的调用，温度调整为0.1确保稳定输出
    """
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            response = client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {"role": "system", "content": "你是一位专业的辩论赛裁判"},
                    {"role": "user", "content": f"{prompt}"},
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API调用失败 ({attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return "API调用失败，请检查网络连接和API密钥"


class ScoringSystem:
    @staticmethod
    def llm_calculate_dimension_scores(speech: dict, history: List[dict], topic: str) -> Dict[str, float]:
        """
        计算辩论发言的多维度分数（0-1范围）
        :param speech: 当前发言 {content: str, stage: str}
        :param history: 历史发言列表
        :param topic: 辩题
        :return: 各维度分数字典
        """
        content = speech.get("content", "")
        stage = speech.get("stage", "质询阶段")

        prompt = ScoringSystem._create_scoring_prompt(content, history, topic, stage)

        try:
            response = llm_api(prompt)

            scores = ScoringSystem._parse_scores(response)
        except Exception as e:
            print(f"评分失败: {str(e)}")
            scores = {
                "logic": 0.5,
                "persuasion": 0.5,
                "relevance": 0.5,
                "clarity": 0.5,
                "depth": 0.5
            }


        stage_weights = {
            "立论阶段": 0.9,
            "质询阶段": 1.0,
            "自由辩论阶段": 1.0,
            "结辩阶段": 0.95
        }
        weight = stage_weights.get(stage, 1.0)

        for key in scores:
            scores[key] = max(0, min(1, round(scores[key] * weight, 2)))

        return scores

    @staticmethod
    def _create_scoring_prompt(content: str, history: List[dict], topic: str, stage: str) -> str:
        """
        创建评分提示词
        """
        history_summary = ScoringSystem._summarize_history(history)

        return f"""
    ### 辩论裁判评分任务 ###
    辩题: {topic}
    当前阶段: {stage}
    历史发言摘要:
    {history_summary}
    
    ###当前发言内容:
    {content}
    
    ###请一步步思考当前辩手发言内容以及过往发言历史，从以下5个维度对当前发言进行评分（0.0-1.0），每个维度分数必须是0到1之间的浮点数：
    1. 逻辑性 (logic): 论证结构是否严密，推理是否合理
    2. 说服力 (persuasion): 论据是否有力，能否有效说服听众
    3. 相关性 (relevance): 内容是否紧扣辩题，回应历史论点
    4. 清晰度 (clarity): 表达是否清晰易懂，条理分明
    5. 深度 (depth): 论点是否有思想深度和洞察力
    
    ###请严格按照JSON格式返回结果，仅包含分数值:
    {{
        "logic": 0.0,
        "persuasion": 0.0,
        "relevance": 0.0,
        "clarity": 0.0,
        "depth": 0.0
    }}
    ###再次重复，你只能严格按照JSON格式返回结果，仅仅包含分数值，不能输出除了分数值之外的任何结果!!!
    """

    @staticmethod
    def _parse_scores(response: str) -> Dict[str, float]:
        """
        解析API返回的分数
        """
        try:
            scores = json.loads(response.strip())

            required_keys = ["logic", "persuasion", "relevance", "clarity", "depth"]
            if not all(key in scores for key in required_keys):
                raise ValueError("返回格式缺少必要维度")

            for key, value in scores.items():
                if not (0.0 <= float(value) <= 1.0):
                    raise ValueError(f"分数 {key}={value} 超出0-1范围")

            return scores

        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析评分失败: {str(e)}")
            print(f"原始响应: {response}")
            # 我们目前设置的prompt能够让AI大致按照我们规定的格式返回，但是如果实在返回了其他东西，就按0.5来评分（出现了额外的东西一般是输入内容有很怪的东西）
            return {key: 0.5 for key in required_keys}

    @staticmethod
    def _summarize_history(history: list) -> str:
        """
        综合发言历史
        """
        if not history:
            return "暂无历史发言"

        return "\n".join(
            f"{idx + 1}. {item.get('role', '辩手')}: {item.get('content', '')[:80]}{'...' if len(item.get('content', '')) > 80 else ''}"
            for idx, item in enumerate(history[-3:])
        )

    @staticmethod
    def calculate_dimension_scores(speech: dict, history: List[dict], topic: str) -> Dict[str, float]:
        """
        Calculate multi-dimensional scores for debate speech
        :param speech: Current speech {content: str}
        :param history: List of historical speeches
        :param topic: Debate topic
        :return: Dictionary of dimension scores
        """
        content = speech.get("content", "")
        
        # 从逻辑\说服力\相关性\清晰度\深度，五个方面对于发言内容进行评分
        scores = {
            "logic": ScoringSystem._calculate_logic_score(content),
            "persuasion": ScoringSystem._calculate_persuasion_score(content),
            "relevance": ScoringSystem._calculate_relevance(content, history, topic),
            "clarity": ScoringSystem._calculate_clarity_score(content),
            "depth": ScoringSystem._calculate_depth_score(content),
        }
        
        #  scoring weights
        stage_weights = {
            "立论阶段": 0.9,   
            "质询阶段": 1.0,   
            "自由辩论阶段": 1.0, 
            "结辩阶段": 0.95   
        }
        stage = speech.get("stage", "质询阶段")
        weight = stage_weights.get(stage, 1.0)
        for key in scores:
            scores[key] = round(scores[key] * weight, 2)
        
        return scores
    
    @staticmethod
    def _calculate_logic_score(content: str) -> float:
        """
        """
        logic_words = [
            "因为", "所以", "因此", "然而", "但是", "尽管", "既然", "故而", "由此可见", "综上所述",
            "首先", "其次", "再者", "最后", "一方面", "另一方面", "相反", "反之", "倘若", "假如",
            "假设", "那么", "则", "并且", "而且", "同时", "此外", "另外", "不仅如此", "更重要的是",
            "关键", "本质上", "实质上", "归根结底", "简而言之", "总而言之", "也就是说", "换言之",
            "例如", "比如", "举例来说", "为例", "相比之下", "相对而言", "毫无疑问", "显然", "显然地",
            "必然", "必定", "不可避免地", "结果", "导致", "引起", "造成", "产生", "源于", "源自"
        ]
        word_list = jieba.lcut(content)
        
        logic_count = sum(1 for word in word_list if word in logic_words)
        
        return min(0.3 + logic_count * 0.1, 0.9)
    
    @staticmethod
    def _calculate_persuasion_score(content: str) -> float:
        """
        """
        positive_words = [
            "必须", "应该", "证明", "显然", "确保", "保障", "有益", "促进", "提升", "增强",
            "改善", "进步", "发展", "创新", "突破", "优势", "益处", "价值", "意义", "重要",
            "必要", "关键", "核心", "根本", "有利", "积极", "正面", "建设性", "可行性", "可靠性",
            "稳定", "安全", "高效", "有效", "成功", "成就", "胜利", "解决", "克服", "超越",
            "领先", "卓越", "优秀", "出色", "显著", "明显", "充分", "全面", "完善", "成熟"
        ]
        negative_words = [
            "不能", "不该", "危害", "破坏", "威胁", "损害", "阻碍", "削弱", "限制", "问题",
            "缺陷", "不足", "缺点", "弊端", "风险", "危机", "挑战", "困难", "障碍", "矛盾",
            "冲突", "对立", "负面", "消极", "不利", "有害", "危险", "不可行", "不可靠", "不稳定",
            "不安全", "低效", "无效", "失败", "挫折", "困境", "恶化", "衰退", "落后", "劣势",
            "缺乏", "缺失", "不足", "不充分", "不完善", "不成熟", "复杂", "混乱", "模糊", "不确定"
        ]
        
        pos_count = sum(content.count(word) for word in positive_words)
        neg_count = sum(content.count(word) for word in negative_words)
        
        base = 0.5
        emotion_score = min(pos_count * 0.05 + neg_count * 0.04, 0.4)
        
        return base + emotion_score
    
    @staticmethod
    def _calculate_relevance(content: str, history: List[dict], topic: str) -> float:
        """
        """
        if not content:
            return 0.0
            
        topic_words = set(jieba.lcut(topic))
        content_words = set(jieba.lcut(content))
        
        # Jaccard-simularity
        if topic_words:
            topic_match = len(topic_words & content_words) / len(topic_words) 
        else:
            topic_match = 0.7  

        context_score = 0
        if history:
            recent_history = history[-3:]
            history_text = " ".join([h.get("content", "") for h in recent_history])
            history_words = set(jieba.lcut(history_text))
            
            intersection = len(content_words & history_words)
            union = len(content_words | history_words)
            context_score = intersection / union if union > 0 else 0

        return round(0.3 * topic_match + 0.7 * context_score, 2)
    
    @staticmethod
    def _calculate_clarity_score(content: str) -> float:
        """
        """
        sentences = [s for s in content.split("。") if s] or [content]
        avg_length = sum(len(sent) for sent in sentences) / len(sentences)
        
        if avg_length < 15:
            return 0.9
        elif avg_length < 25:
            return 0.7
        else:
            return 0.5
    
    @staticmethod
    def _calculate_depth_score(content: str) -> float:
        """
        """
        professional_terms = [
            "量化", "实证", "辩证法", "方法论", "范式", "理论", "原理", "机理", "本质", "内涵", "外延", "变量",
            "因果关系", "相关性", "回归分析","定理", "公理", "标准差", "显著性", "置信区间", "假设检验", "控制变量",
            "自变量", "因变量", "中介变量", "调节变量", "信度", "效度", "分析", "抽样", "样本", "总体",
            "参数", "统计量", "正态分布", "偏态", "峰度", "方差分析", "协方差", "研究", "回归系数", "标准化",
            "概念化", "操作化", "理论框架", "研究设计", "文献综述", "元分析", "系统评价", "报告", "质性研究",
            "定量研究", "混合方法", "三角验证", "扎根理论", "内容分析", "话语分析", "民族志", "现象学",
            "心理学", "潜意识", "认知失调", "条件反射", "社会认同", "自我实现", "心理防御机制", "集体无意识", 
            "认知行为疗法", "情绪智力", "人格特质", "依恋理论", "操作性条件反射","经济学", 
            "机会成本", "边际效用", "市场失灵", "外部性", "通货膨胀", "货币政策", "财政政策", 
            "比较优势", "博弈论", "供需曲线", "凯恩斯主义", "货币主义","计算机科学",
            "机器学习", "神经网络", "算法复杂度", "数据结构", "递归函数", "面向对象", "云计算", 
            "区块链", "分布式系统", "深度学习", "自然语言处理", "计算机视觉","生物学",
            "基因表达", "自然选择", "细胞分裂", "生态系统", "生物多样性", "光合作用", "DNA复制", 
            "蛋白质合成", "进化论", "遗传密码", "免疫应答", "神经递质","物理学",
            "量子纠缠", "相对论", "熵增原理", "电磁感应", "波粒二象性", "热力学定律", "引力透镜", 
            "夸克模型", "弦理论", "暗物质", "宇宙膨胀", "量子隧穿", "法学",
            "无罪推定", "司法审查", "程序正义", "实体权利", "法律保留", "比例原则", "法律漏洞", 
            "司法解释", "法律事实", "法律行为", "法律关系", "法律冲突", "教育学", 
            "建构主义", "多元智能", "形成性评价", "翻转课堂", "差异化教学", "学习迁移", "教育公平", 
            "全纳教育", "终身学习", "课程统整", "教学反思", "教育评价","医学", 
            "病理", "生理", "循证医学", "免疫疗法", "基因编辑", "精准医疗", "抗生素耐药", "流行病学", 
            "症状管理", "预防医学", "康复治疗", "姑息治疗", "医患沟通", "政治学", 
            "权力制衡", "民主集中制", "软实力", "地缘政治", "意识形态", "公共政策", "治理能力", 
            "公民社会", "政治社会化", "选举制度", "政治参与", "政治文化", "环境科学", 
            "碳中和", "生物降解", "生态系统服务", "可持续发展", "碳足迹", "生物多样性", "环境承载力", 
            "污染治理", "气候变化", "可再生能源", "生态修复", "环境正义"
        ]
        
        term_count = sum(content.count(term) for term in professional_terms)
        base = 0.4
        term_score = min(term_count * 0.1, 0.5)
        return base + term_score