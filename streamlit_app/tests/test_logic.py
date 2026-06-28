"""
API 키 없이 돌릴 수 있는 순수 로직 스모크 테스트.
실행: cd streamlit_app && python3 -m pytest tests/ -v  (또는 python3 tests/test_logic.py)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules import data_loader, patient_chat, grading


def test_data_loader():
    cb = data_loader.load_case_bank()
    ids = data_loader.list_case_ids(cb)
    assert len(ids) == 23
    assert "acute_01" in ids
    case = data_loader.get_case(cb, "acute_01")
    assert case["case_id"] == "acute_01"
    key = data_loader.get_key_items("acute_01")
    assert "hx" in key and "pe" in key


def test_parse_bracket_action():
    assert patient_chat.parse_bracket_action("(우하복부를 눌러본다)") is True
    assert patient_chat.parse_bracket_action("배가 언제부터 아프셨어요?") is False
    assert patient_chat.parse_bracket_action("  (DRE 수행)  ") is True


def test_build_patient_system_prompt():
    cb = data_loader.load_case_bank()
    case = data_loader.get_case(cb, "acute_01")
    prompt = patient_chat.build_patient_system_prompt(case)
    assert case["patient"]["name"] in prompt
    assert case["chief_complaint"] in prompt
    assert "괄호" in prompt


def test_build_grading_prompt():
    cb = data_loader.load_case_bank()
    case = data_loader.get_case(cb, "acute_01")
    chat_log = [
        {"role": "doctor", "text": "언제부터 아프셨어요?"},
        {"role": "patient", "text": "어제부터요."},
        {"role": "exam", "text": "[진찰: 우하복부 압통 확인]"},
        {"role": "patient", "text": "아 거기 누르니까 아파요!"},
    ]
    diagnosis_form = {"impression": "급성 충수돌기염", "tests": "복부 CT", "treatments": "외과 의뢰"}
    prompt = grading.build_grading_prompt(case, chat_log, diagnosis_form)
    assert "급성 충수돌기염" in prompt
    assert "[의사] 언제부터 아프셨어요?" in prompt
    assert "[환자] 어제부터요." in prompt
    assert '"total": 0' in prompt


if __name__ == "__main__":
    test_data_loader()
    test_parse_bracket_action()
    test_build_patient_system_prompt()
    test_build_grading_prompt()
    print("ALL TESTS PASSED")
