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