# app/api/routes.py
from fastapi import FastAPI
from app.core.path_resolver import PathResolver, load_fields_config
from app.core.rule_loader import load_rules
from app.core.rule_dispatcher import RuleDispatcher

app = FastAPI(title="Mortgage Rule Engine API")

@app.post("/validate")
def validate(payload: dict):
    """
    Payload expected to be the combined context:
    {
      "los": { ... },
      "title": { ... },
      "appraisal": { ... },
      "credit_report": { ... },
      "drive_report": { ... }
    }
    """
    resolver = PathResolver(load_fields_config())
    rules = load_rules()
    dispatcher = RuleDispatcher(resolver=resolver, rules=rules)
    results = dispatcher.evaluate(payload)
    return {"loan_id": payload.get('los', {}).get('loan_id'), "results": results}
