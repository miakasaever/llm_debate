# AI Debate Simulator

一个基于大语言模型的辩论赛模拟系统，支持AI辩手自动辩论和玩家参与模式，包含多维度裁判评分机制。

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
   - 选择AI模型（支持阿里云DashScope模型）

## 安装指南

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/ai-debate-simulator.git
cd ai-debate-simulator
