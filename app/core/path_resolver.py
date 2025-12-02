# app/core/path_resolver.py
import os
import yaml
from typing import Any, Dict

def load_fields_config(path: str = None) -> Dict[str, Dict]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'config', 'fields.yaml')
    with open(path, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)

class PathResolver:
    def __init__(self, fields_config: Dict[str, Dict] = None):
        self.fields = fields_config or load_fields_config()

    def _get_field_info(self, collection: str, logical_name: str) -> Dict[str, Any]:
        coll = self.fields.get(collection, {})
        return coll.get(logical_name, {})

    def resolve(self, context: Dict[str, Any], collection: str, logical_name: str) -> Any:
        """
        Resolve logical_name in given collection from context using fields.yaml mapping.
        If path not found or data not present, returns the configured default.
        """
        info = self._get_field_info(collection, logical_name)
        path = info.get('path')
        default = info.get('default')
        if not path:
            return default
        # navigation: dotted path
        cur = context.get(collection, {})
        for part in path.split('.'):
            if isinstance(cur, dict) and part in cur:
                cur = cur.get(part)
            else:
                return default
        return cur if cur is not None else default

    def resolve_any(self, context: Dict[str, Any], logical_name: str) -> Any:
        """
        Try resolving logical_name across collections in priority order.
        """
        for coll in ['los', 'title', 'appraisal', 'credit_report', 'drive_report']:
            val = self.resolve(context, coll, logical_name)
            if val not in [None, "", []]:
                return val
        return None
