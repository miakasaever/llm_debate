# ----------------------------------------------------------
# main.py
#
#
#
# ----------------------------------------------------------

import os
import random
import time
import argparse
from typing import List, Dict
from agents.debater_agent import DebaterAgent
from agents.referee_agent import RefereeAgent
from agents.player_agent import PlayerAgent
from utils.config_loader import ConfigLoader

DEBATE_STAGES = [
    {"name": "立论阶段", "order": "sequential", "rounds": 1},
    {"name": "质询阶段", "order": "cross", "rounds": 2},
    {"name": "自由辩论阶段", "order": "random", "rounds": 3},
    {"name": "结辩阶段", "order": "sequential", "rounds": 1}
]


class DebateSimulator:
    def __init__(self, topic: str, roles: List[str], config: Dict,ai_used: bool,nums_of_referee:int, player_roles: List[str] = []):
        self.topic = topic
        self.roles = roles
        self.config = config
        self.ai_used = ai_used
        self.nums_of_referee=nums_of_referee
        self.player_roles = player_roles or []
        self.agents = self._create_agents()
        self.speech_history = []
        self.current_stage = 0



    def _create_debate_agents(self,agents:List[Dict]):
        for role in self.roles:
            agent_id = f"debater_{len(agents)}"
            config = {
                "knowledge_agent": self.config.get("debate_agent_config", {}).get(role,{}),
                "max_speech_length": self.config.get("max_speech_length", 800)
            }
            if role in self.player_roles:
                agent = PlayerAgent(agent_id, role, config)
                agent_type = "player"
            else:
                agent = DebaterAgent(agent_id, role, config)
                agent_type = "debater"

            agents.append({
                "id": agent_id,
                "agent": agent,
                "type": agent_type,
                "role": role,
                "team": role[:2]
            })



    def _create_referee_agents(self,agents:List[Dict]):
        for i in range(self.nums_of_referee):
            referee_config = {
                "knowledge_agent": self.config.get("debate_agent_config", {}).get(f"裁判{i+1}",{})
            }
            referee_agent = RefereeAgent(f"referee_{i+1}", f"裁判{i+1}", referee_config, self.ai_used)
            agents.append({
                "id": f"referee_{i+1}",
                "agent": referee_agent,
                "type": "referee",
                "role": f"裁判{i+1}"
            })


    def _create_agents(self) -> List[Dict]:
        """
        初始化智能体
        """
        agents = []

        self._create_debate_agents(agents)
        self._create_referee_agents(agents)

        return agents

    def run_debate(self):
        """
        辩论赛主程序
        """
        print(f"\n{'=' * 50}")
        print(f"辩论开始！主题: {self.topic}")
        print(f"Player-controlled roles: {', '.join(self.player_roles)}")
        print(f"{'=' * 50}\n")

        for stage_index, stage in enumerate(DEBATE_STAGES):
            self.current_stage = stage_index
            stage_name = stage["name"]
            stage_rounds = stage["rounds"]

            print(f"\n{'=' * 50}")
            print(f"当前阶段: {stage_name} (轮次: {stage_rounds})")
            print(f"{'=' * 50}")

            for round_num in range(1, stage_rounds + 1):
                print(f"\n--- Round {round_num} ---")

                # 根据不同阶段调整不同的顺序
                debaters = [a for a in self.agents if a["type"] in ["debater", "player"]]

                if stage["order"] == "sequential":
                    # 顺序发言
                    speaker_order = debaters
                elif stage["order"] == "cross":
                    # 交叉发言
                    pro_debaters = [d for d in debaters if d["team"] == "正方"]
                    con_debaters = [d for d in debaters if d["team"] == "反方"]
                    speaker_order = []
                    for i in range(max(len(pro_debaters), len(con_debaters))):
                        if i < len(pro_debaters):
                            speaker_order.append(pro_debaters[i])
                        if i < len(con_debaters):
                            speaker_order.append(con_debaters[i])
                else:
                    # 随机排序发言
                    random.shuffle(debaters)
                    speaker_order = debaters

                # 合成发言
                for agent_info in speaker_order:
                    context = {
                        "topic": self.topic,
                        "current_stage": stage_name,
                        "stage_round": round_num,
                        "speech_history": self.speech_history
                    }

                    response = agent_info["agent"].generate_response(context)
                    self.speech_history.append(response)

                    if agent_info["type"] == "player":
                        print(f"\n【{agent_info['role']}】(玩家)发言：")
                    else:
                        print(f"\n【{agent_info['role']}】(AI)截断后发言：")
                    print(f"{response['content']}")

                    # 收集信息交由裁判系统判断
                    referees = [a for a in self.agents if a["type"] == "referee"]
                    for referee in referees:
                        judge_context = {
                            "topic": self.topic,
                            "current_stage": stage_name,
                            "stage_round": round_num,
                            "speech_history": self.speech_history,
                            "current_speech": response
                        }
                        judgment = referee["agent"].generate_response(judge_context)
                        self.speech_history.append(judgment)

                        print(f"\n【{referee['role']}】评分:")
                        for dim, score in judgment["scores"].items():
                            print(f"  {dim}: {score:.2f}")
                        print(f"Comment: {judgment['comment']}")

                    time.sleep(2)

        self.announce_result()

    def announce_result(self):
        """
        计算分数并最后得出结果
        """
        team_scores = {"正方": 0, "反方": 0}
        team_counts = {"正方": 0, "反方": 0}

        # 开始评分
        for speech in self.speech_history:
            if speech["type"] == "judgment":
                prev_idx = self.speech_history.index(speech) - 1
                if prev_idx >= 0 and self.speech_history[prev_idx]["type"] == "argument":
                    debater_speech = self.speech_history[prev_idx]
                    team = debater_speech["role"][:2]
                    if team in team_scores:
                        total_score = sum(speech["scores"].values())
                        team_scores[team] += total_score
                        team_counts[team] += 1

        # 计算平均分数
        team_avg = {}
        for team, total in team_scores.items():
            if team_counts[team] > 0:
                team_avg[team] = total / team_counts[team]
            else:
                team_avg[team] = 0

        # 展示结果
        print("\n" + "=" * 50)
        print("辩论结束！最终结果：")
        print("=" * 50)
        print(f"正方平均分: {team_avg.get('正方', 0):.2f}")
        print(f"反方平均分: {team_avg.get('反方', 0):.2f}")

        # 判断胜者
        if team_avg["正方"] > team_avg["反方"]:
            print("\n胜方: 正方！")
        elif team_avg["反方"] > team_avg["正方"]:
            print("\n胜方: 反方！")
        else:
            print("\n平局！")
        print("=" * 50)


def main():
    '''
    主程序
    '''

    parser = argparse.ArgumentParser(description='AI Debate Simulator')
    parser.add_argument('--topic', type=str, default="人工智能是否威胁人类就业",
                        help='Debate topic')
    #Use your API_KEY as possible
    parser.add_argument('--api_key', type=str, default=os.getenv("DASHSCOPE_API_KEY"),
                        help='DashScope API key (can also be set via environment variable)')

    parser.add_argument('--model', type=str, default="qwen-plus",
                        help='AI model to use')

    parser.add_argument('--roles', nargs='+',
                        default=["正方一辩", "反方一辩", "正方二辩", "反方二辩","正方三辩","反方三辩","正方四辩","反方四辩"],
                        help='List of debater roles')
    parser.add_argument('--player_roles', nargs='+',
                        choices=["正方一辩", "反方一辩", "正方二辩", "反方二辩","正方三辩","反方三辩","正方四辩","反方四辩"],
                        help='Roles controlled by human players')
    #Setting it True would be better
    parser.add_argument('--nums_referee',
                        type=int,
                        default=1,
                        help='Number of referee'
    )
    parser.add_argument('--ai_use',
                        type=bool,
                        default=True,
                        help='Ai referee used or not'),
    args = parser.parse_args()

    config = ConfigLoader.load_config()
    knowledge_config = {
        "api_key": args.api_key,
        "model": args.model
    }
    config["knowledge_agent_config"] = knowledge_config

    #Create debate_agent_config
    agents_config=ConfigLoader.create_model_config(args.roles,args.nums_referee)
    config['debate_agent_config']=agents_config

    # Init
    player_roles = args.player_roles or []
    print(f"使用模型: {args.model}")
    print(f"辩手角色: {', '.join(args.roles)}")
    print(f"玩家控制的角色: {', '.join(player_roles) if player_roles else '无'}")
    simulator = DebateSimulator(args.topic, args.roles, config, args.ai_use,args.nums_referee,player_roles=player_roles)
    simulator.run_debate()

if __name__ == "__main__":
    main()
