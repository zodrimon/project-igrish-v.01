import pytest
from app.core.classification import AppClassifier
import os
import json

def test_app_classifier_default(tmp_path):
    rules = {
        "coding": ["code.exe"],
        "distraction": ["youtube"]
    }
    config_file = tmp_path / "classification_rules.json"
    with open(config_file, "w") as f:
        json.dump(rules, f)
        
    classifier = AppClassifier(config_path=str(config_file))
    
    assert classifier.classify("code.exe", "some project") == "coding"
    assert classifier.classify("chrome.exe", "YouTube - video") == "distraction"
    assert classifier.classify("unknown.exe", "Unknown Window") == "unknown"
    assert classifier.classify(None, None) == "unknown"
