# tests/test_engine.py
import json
from app.core.path_resolver import PathResolver, load_fields_config
from app.core.rule_loader import load_rules
from app.core.rule_dispatcher import RuleDispatcher

def run_test():
    ctx = json.load(open('tests/dummy_data.json', 'r', encoding='utf-8'))
    resolver = PathResolver(load_fields_config())
    rules = load_rules()
    dispatcher = RuleDispatcher(resolver=resolver, rules=rules)
    results = dispatcher.evaluate(ctx)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_test()
