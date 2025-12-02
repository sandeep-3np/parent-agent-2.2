# app/core/rule_dispatcher.py
from typing import List, Dict, Any
from importlib import import_module
from .rule_loader import load_rules
from .path_resolver import PathResolver, load_fields_config

class RuleDispatcher:
    def __init__(self, resolver: PathResolver = None, rules: List[Dict[str, Any]] = None):
        self.resolver = resolver or PathResolver(load_fields_config())
        self.rules = rules or load_rules()

        # Load validators module
        try:
            self.validators_mod = import_module('app.validators.validators')
        except Exception:
            self.validators_mod = import_module('app.validators')

    def _token_gt(self, token: str, value: Any) -> bool:
        """Interpret tokens like 'GT80' => value > 80."""
        token = str(token)
        if token.upper().startswith('GT'):
            try:
                threshold = float(token[2:])
            except:
                return False
            try:
                v = float(value)
                if v <= 1:
                    v = v * 100
                return v > threshold
            except:
                return False
        return False

    # ---------------------------------------------------------------
    # NEW: OR SUPPORT + Helper Methods
    # ---------------------------------------------------------------

    def _check_trigger_single(self, key: str, allowed, context: Dict[str, Any]) -> bool:
        """Checks a single trigger field."""

        if not isinstance(allowed, list):
            allowed = [allowed]

        matched_any = False

        for coll in ['los', 'title', 'appraisal', 'credit_report', 'drive_report']:
            val = self.resolver.resolve(context, coll, key)
            if val is None or val == "":
                continue

            # ANY = match if the field is present
            if any(str(a).upper() == 'ANY' for a in allowed):
                matched_any = True
                break

            # GT tokens
            for a in allowed:
                if isinstance(a, str) and a.upper().startswith('GT'):
                    if self._token_gt(a, val):
                        matched_any = True
                        break
                else:
                    # direct equality or intersection
                    if isinstance(val, list):
                        if any(str(x) == str(a) for x in val):
                            matched_any = True
                            break
                    else:
                        if str(val).strip() == str(a).strip():
                            matched_any = True
                            break

            if matched_any:
                break

        return matched_any

    def _check_trigger_block(self, block: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Checks a block of triggers (AND inside a single OR block)."""
        for key, allowed in block.items():
            if not self._check_trigger_single(key, allowed, context):
                return False
        return True

    # ---------------------------------------------------------------
    # UPDATED _check_trigger WITH OR SUPPORT
    # ---------------------------------------------------------------
    def _check_trigger(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Supports:
            - Regular AND triggers
            - OR block:
                trigger:
                  or:
                    - field1: [values]
                    - field2: [values]
        """

        trigger = rule.get('trigger') or {}

        # 1. OR BLOCK SUPPORT
        or_blocks = trigger.get("or")
        if or_blocks:
            or_matched = False
            for block in or_blocks:
                # Each OR block is an AND block internally
                if self._check_trigger_block(block, context):
                    or_matched = True
                    break
            if not or_matched:
                return False

        # 2. NORMAL AND TRIGGERS (skip "or" key)
        for key, allowed in trigger.items():
            if key == "or":
                continue
            if not self._check_trigger_single(key, allowed, context):
                return False

        return True

    # ---------------------------------------------------------------

    def _get_validator(self, name: str):
        cls = getattr(self.validators_mod, name, None)
        if cls is None:
            raise Exception(f"Validator '{name}' not found.")
        return cls()

    def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for rule in self.rules:
            try:
                triggered = self._check_trigger(rule, context)
                if not triggered:
                    results.append({
                        'rule_id': rule.get('id'),
                        'status': 'NOT_APPLICABLE',
                        'message': '',
                        'details': {}
                    })
                    continue

                validator_name = rule.get('validator')
                validator = self._get_validator(validator_name)
                res = validator.evaluate(rule, context, self.resolver)
                results.append(res)

            except Exception as e:
                results.append({
                    'rule_id': rule.get('id'),
                    'status': 'ERROR',
                    'message': str(e),
                    'details': {}
                })
        return results
