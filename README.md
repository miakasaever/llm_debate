#llm_debate一个辩论赛模拟系统
概述
这是一个高级AI辩论赛模拟系统，支持多人辩论、自定义裁判数量、玩家参与以及AI裁判功能。系统模拟完整的辩论流程（立论、质询、自由辩论和结辩阶段），提供基于规则评分和AI评分两种模式，支持为每个角色配置不同的大模型。

功能亮点
多角色支持：无限支持辩手

灵活裁判系统：可配置多名裁判同时评分，支持AI裁判模式（建议使用）

模型定制：为每个辩手和裁判单独配置不同的大模型

双模式评分：基于规则的评分和AI评分两种模式

完整辩论流程：立论、质询、自由辩论和结辩四个阶段（同时，辩论的流程也可以根据个人的需要进行调整）

玩家参与：可选择扮演特定辩论角色

安装指南
依赖安装
bash
pip install openai jieba argparse
环境配置
获取DashScope API密钥：

访问 https://dashscope.console.aliyun.com/

创建账号并获取API密钥

设置环境变量：

bash
# Linux/MacOS
export DASHSCOPE_API_KEY='your_api_key_here'

# Windows
set DASHSCOPE_API_KEY='your_api_key_here'
使用说明
基本命令
bash
python main.py --topic "辩论主题" --roles 正方一辩 反方一辩 --ai_use True
完整命令行参数
参数	说明	默认值	示例
--topic	辩论主题	"人工智能是否威胁人类就业"	--topic "远程工作是否比办公室工作更高效"
--roles	辩手角色	["正方一辩", "反方一辩", "正方二辩", "反方二辩"]	--roles 正方一辩 反方一辩 正方二辩
--player_roles	玩家控制的角色	[]	--player_roles 正方一辩
--model	默认大模型	"qwen-plus"	--model qwen-max
--nums_referee	裁判人数	1	--nums_referee 3
--ai_use	是否使用AI裁判	True	--ai_use False
--api_key	DashScope API密钥	从环境变量获取	--api_key sk-xxxxxx
完整示例
bash
python main.py \
  --topic "人工智能是否会有自我意识" \
  --roles 正方一辩 反方一辩 正方二辩 反方二辩 \
  --player_roles 反方一辩 \
  --model qwen-max \
  --nums_referee 3 \
  --ai_use True
