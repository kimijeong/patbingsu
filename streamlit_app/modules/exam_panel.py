"""
담당: 개발자 B
동작하는 최소 버전임 (4분할 버튼 → 진찰 선택 → 환자봇 호출까지 연결됨).
TODO(자유): 그리드 디자인/아이콘, 괄호 자유 입력 행동과의 시각적 구분 등 다듬기.
시그니처/session_state 키는 CONTRACT.md 기준으로 고정되어 있으니 바꾸려면 셋이 합의 후 변경.
"""
import streamlit as st
from . import patient_chat

ZONES = {"RUQ": "우상복부", "LUQ": "좌상복부", "RLQ": "우하복부", "LLQ": "좌하복부"}
ACTIONS = ["압통 확인", "반발통 확인", "특수 진찰"]


def render_exam_panel(case: dict) -> None:
    st.subheader("복부 진찰")
    # TODO(개발자 B): 2x2 그리드 버튼 + 부위별 서브 선택(압통/반발통/특수진찰) UI 구체화.
    # 아래는 동작하는 최소 골격(버튼 4개 + selectbox). 디자인/레이아웃 자유롭게 개선 가능.
    cols = st.columns(2)
    zone_keys = list(ZONES.keys())
    for i, zone in enumerate(zone_keys):
        col = cols[i % 2]
        with col:
            if st.button(ZONES[zone], key=f"exam_{zone}", use_container_width=True):
                st.session_state[f"_pending_zone"] = zone

    pending_zone = st.session_state.get("_pending_zone")
    if pending_zone:
        action = st.selectbox(
            f"{ZONES[pending_zone]} - 어떤 진찰을 할까요?",
            ACTIONS,
            key="_pending_action",
        )
        if st.button("진찰 시행", key="_confirm_exam"):
            on_exam_action(pending_zone, action)
            st.session_state["_pending_zone"] = None
            st.rerun()

    # TODO(개발자 B): 괄호 텍스트 "(DRE 수행)" 같은 자유 입력 행동도 채팅 입력창에서
    # patient_chat.parse_bracket_action()으로 감지되도록 app.py 쪽 입력 처리와 연동 확인.


def on_exam_action(zone: str, action: str) -> None:
    """4분할 버튼 클릭 → exam_log 기록 + chat_log에 시스템 신호 추가 + 환자봇 호출."""
    note = f"[진찰: {ZONES[zone]} {action}]"
    st.session_state.exam_log.append({"zone": zone, "action": action, "note": note})
    st.session_state.chat_log.append({"role": "exam", "text": note})

    case = st.session_state.case
    sys_prompt = patient_chat.build_patient_system_prompt(case)
    messages = patient_chat._chat_log_to_messages(st.session_state.chat_log)
    reply = patient_chat.call_claude(sys_prompt, messages, st.session_state.api_key, st.session_state.model)
    st.session_state.chat_log.append({"role": "patient", "text": reply})
