# app/core/rule_loader.py
import os
import yaml
from typing import List, Dict, Any

def load_rules(path: str = None) -> List[Dict[str, Any]]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rules.yaml')
    with open(path, 'r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh)
    return data.get('rules', [])
