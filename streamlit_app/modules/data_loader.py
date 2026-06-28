"""
담당: 개발자 A
다른 두 모듈이 의존하므로 제일 먼저 완성할 것. (이미 구현 완료 — 그대로 써도 됨)
"""
import json
import os

_CASE_BANK_CACHE = None
_KEY_ITEMS_CACHE = None

_DEFAULT_CASE_BANK_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "case_bank.json")
_DEFAULT_KEY_ITEMS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "key_items.json")


def load_case_bank(path: str = _DEFAULT_CASE_BANK_PATH) -> dict:
    global _CASE_BANK_CACHE
    if _CASE_BANK_CACHE is None:
        with open(path, encoding="utf-8") as f:
            _CASE_BANK_CACHE = json.load(f)
    return _CASE_BANK_CACHE


def list_case_ids(case_bank: dict) -> list:
    return [c["case_id"] for c in case_bank["cases"]]


def get_case(case_bank: dict, case_id: str) -> dict:
    for c in case_bank["cases"]:
        if c["case_id"] == case_id:
            return c
    raise KeyError(f"case_id not found: {case_id}")


def get_key_items(case_id: str, path: str = _DEFAULT_KEY_ITEMS_PATH) -> dict:
    """케이스별 핵심 병력/진찰 포인트. 채점 프롬프트에서 사용. {"hx": str, "pe": str}"""
    global _KEY_ITEMS_CACHE
    if _KEY_ITEMS_CACHE is None:
        with open(path, encoding="utf-8") as f:
            _KEY_ITEMS_CACHE = json.load(f)
    return _KEY_ITEMS_CACHE.get(case_id, {"hx": "", "pe": ""})


if __name__ == "__main__":
    # 빠른 동작 확인용
    cb = load_case_bank()
    ids = list_case_ids(cb)
    print(f"loaded {len(ids)} cases, first: {ids[0]}")
    c = get_case(cb, "acute_01")
    print(c["chief_complaint"])
    print(get_key_items("acute_01"))
