# studio_toolkit/rate_limiter/__init__.py

from .manager import global_rate_limiter

def get_safe(obj):
    """
    自動判別並回傳帶限速功能的物件
    """
    return global_rate_limiter.get(obj)
