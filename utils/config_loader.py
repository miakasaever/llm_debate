# scoring_system.py

import json
import os

class ConfigLoader:
    @staticmethod
    def load_config(file_path: str = "config.json") -> dict:
        """
        :param file_path: 
        :return: 
        """
        if not os.path.exists(file_path):
            return {
                "max_turn": 5,
                "speech_time_limit": 120,
                "max_speech_length": 800,
                "knowledge_validation": True,
                "scoring_weights": {
                    "logic": 0.25,
                    "persuasion": 0.3,
                    "relevance": 0.2,
                    "clarity": 0.15,
                    "depth": 0.1
                }
            }
        
        with open(file_path, 'r') as f:
            return json.load(f)
    @staticmethod
    def create_model_config(roles_list:list,referee:int,file_path:str="model_config.json")->dict:
        """
        :param file_path
        """
        default_models = {
            "辩手": "qwen-turbo",
            "裁判": "qwen-max"
        }
        if os.path.exists(file_path):
            with open(file_path,'r') as f:
                model_config = json.load(f)
        else:
            model_config={}
        for role in roles_list:
            if role not in model_config:
                model_config[role] = input(f"输入{role}使用模型 (默认: {default_models['辩手']}): ") or default_models['辩手']
        for i in range(1,referee+1):
            referee_key=f"裁判{i}"
            if referee_key not in model_config:
                model_config[referee_key] = input(f"输入{referee_key}使用模型 (默认: {default_models['裁判']}): ") or default_models['裁判']
        if not os.path.exists(file_path):
            flag=input("你可以选择同时创建一个新的json文件")
            if flag:
                with open(file_path,'w',encoding='utf-8') as f:
                    json.dump(model_config,f,indent=4)


        return model_config

