import json
import os
from pathlib import Path

class AppClassifier:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to classification_rules.json in the project root
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "classification_rules.json")
            
        self.rules = {}
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
                
    def classify(self, app_name: str, window_title: str) -> str:
        """Classifies the application into a category based on rules."""
        if not app_name and not window_title:
            return "unknown"
            
        app_name_lower = (app_name or "").lower()
        title_lower = (window_title or "").lower()
        
        for category, keywords in self.rules.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in app_name_lower or keyword_lower in title_lower:
                    return category
                    
        return "unknown"
