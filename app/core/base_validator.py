# app/core/base_validator.py
from typing import Dict, Any

class BaseValidator:
    def pass_result(self, rule: Dict[str, Any], details=None):
        return {"rule_id": rule.get("id"), "status": "PASS", "message": "", "details": details or {}}

    def alert_result(self, rule: Dict[str, Any], message=None, details=None):
        return {"rule_id": rule.get("id"), "status": "ALERT", "message": message or rule.get("alert_message",""), "details": details or {}}

    def condition_result(self, rule: Dict[str, Any], message=None, details=None):
        return {"rule_id": rule.get("id"), "status": "CONDITION", "message": message or rule.get("condition_message",""), "details": details or {}}

    def not_applicable_result(self, rule: Dict[str, Any]):
        return {"rule_id": rule.get("id"), "status": "NOT_APPLICABLE", "message": "", "details": {}}
