# app/utils/fuzzy_matcher.py
try:
    from rapidfuzz import fuzz
    def fuzzy_ratio(a, b):
        if a is None or b is None:
            return 0
        return int(fuzz.token_set_ratio(str(a), str(b)))
except Exception:
    import difflib
    def fuzzy_ratio(a, b):
        if a is None or b is None:
            return 0
        return int(difflib.SequenceMatcher(None, str(a), str(b)).ratio() * 100)

def normalize_string(s):
    if s is None:
        return ""
    s = str(s)
    return ''.join(ch.lower() for ch in s if ch.isalnum() or ch.isspace()).strip()
