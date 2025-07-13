# AI Debate Simulator

一个基于大语言模型的辩论赛模拟游戏，支持AI辩手自动辩论和玩家参与模式，包含多维度裁判评分机制。
**只是设计拿来玩的游戏哦！（如果你想拿去训练自己改一下也没问题QAQ）**
### 联系小熊虫(bearischen@gmail.com/2300013202@stu.pku.edu.cn)
![img](https://github.com/miakasaever/llm_debate/blob/main/%E7%86%8A%E8%99%AB.jpg)

## 功能特点

1. **多角色辩论系统**：
   - AI辩手自动生成论点
   - 玩家可参与控制特定辩手
   - 裁判智能评分（支持AI评分和规则评分双模式）

2. **完整辩论流程**：
   - 立论阶段
   - 质询阶段
   - 自由辩论阶段
   - 结辩阶段

3. **智能评分系统**：
   - 逻辑性 (logic)
   - 说服力 (persuasion)
   - 相关性 (relevance)
   - 清晰度 (clarity)
   - 深度 (depth)

4. **高度可配置**：
   - 自定义辩题
   - 调整裁判数量
   - 配置发言长度限制
   - 选择AI模型（支持阿里云DashScope模型,每个Agent都可独立设置模型）

## 安装指南

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/ai-debate-simulator.git
cd ai-debate-simulator 
```
2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 设置环境变量（获取Dashscope API密钥）
```bash
export DASHSCOPE_API_KEY=your_api_key_here
```
## 使用说明
### 基本运行
```bash
python main.py --topic "人工智能是否威胁到人类就业"
```
### 完整选项
```bash
python main.py \
--topic "辩论主题" \
--roles 正方一辩 正方二辩... \ #all debate agents
--play_role 正方一辩 \ #可供选择，无输入则默认全程由AI进行辩论
--nums_referee 1 \ #裁判数量
--ai_used True \ #是否使用AI裁判，推荐默认为True,经验性设计的裁判非常垃圾
```
### 项目结构
```txt
ai-debate-simulator/
├── agents/
│   ├── base_agent.py          # 基础代理类
│   ├── debater_agent.py       # AI辩手实现
│   ├── player_agent.py        # 玩家控制辩手
│   └── referee_agent.py       # 裁判代理
├── utils/
│   ├── config_loader.py       # 配置加载器
│   ├── knowledge_validator.py # 知识验证
│   ├── scoring_system.py      # 评分系统
│   ├── speech_handler.py      # 发言处理器
│   └── __init__.py            # 工具包初始化
├── main.py                    # 主程序入口
└── requirements.txt           # 依赖列表
```

## 配置说明
1. 模型配置
编辑``config.json``控制agent使用model（本程序暂时不支持英文，json文件中直接使用中文的utf-8作为key,如有不适，那就不适AoA）
2. 辩论参数
```json
{
  "max_turn": 5,
  "speech_time_limit": 120,
  "max_speech_length": 800,
  "scoring_weights": {
    "logic": 0.25,
    "persuasion": 0.3,
    "relevance": 0.2,
    "clarity": 0.15,
    "depth": 0.1
  }
}
```
## 贡献指南
### 本项目还有以下可改进的地方
1. 暂不支持英文
2. 每个ai_debate_agent使用的都是同一个prompt，如果要使用该程序在模拟真实辩论场景需要设计拓展性和独立性更强的prompt,同时自行调整debate_order。
3. 暂时只支持使用openai方式调用API
### 欢迎贡献，请遵守以下流程
1. Fork本项目 and and and and and 联系我(bearischen@gmail.com or 2300013202@stu.pku.edu.cn)
2. 创建新分支``git checkout -b feature/your-feature``
3. 提交更改``git commit -am 'Add some feature'``
4. 推送分支``git push origin feature/your-feature``
5. 创建pull request
