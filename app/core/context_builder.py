# app/core/context_builder.py
from typing import Dict, Any

def build_context_from_docs(los: Dict[str, Any] = None,
                            title: Dict[str, Any] = None,
                            appraisal: Dict[str, Any] = None,
                            credit: Dict[str, Any] = None,
                            drive: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Simple builder to assemble the context dict used by the engine.
    In production, these docs come from MongoDB collections.
    """
    ctx: Dict[str, Any] = {}
    ctx['los'] = los or {}
    if title is not None:
        ctx['title'] = title
    if appraisal is not None:
        ctx['appraisal'] = appraisal
    if credit is not None:
        ctx['credit_report'] = credit
    if drive is not None:
        ctx['drive_report'] = drive
    return ctx
