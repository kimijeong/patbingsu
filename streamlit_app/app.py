"""
메인 레이아웃. acute_01 하나만 끝까지 동작하는 게 목표 (나머지 22개는 데이터 구조가 같아 자동 동작).
모듈 셋업/시그니처는 CONTRACT.md 참고.
"""
import streamlit as st
from modules import data_loader, patient_chat, exam_panel, grading

st.set_page_config(page_title="CPX LLM - 복통 시뮬레이터", layout="wide")

# --- 세션 상태 초기화 ---
for key, default in [
    ("case", None),
    ("chat_log", []),
    ("exam_log", []),
    ("diagnosis_form", None),
    ("grading_result", None),
    ("api_key", ""),
    ("model", "claude-haiku-4-5-20251001"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

case_bank = data_loader.load_case_bank()

# --- 사이드바: API 키 / 모델 / 케이스 선택 ---
with st.sidebar:
    st.header("설정")
    st.session_state.api_key = st.text_input("Anthropic API 키", type="password", value=st.session_state.api_key)
    st.session_state.model = st.selectbox(
        "모델",
        ["claude-haiku-4-5-20251001", "claude-sonnet-4-6"],
        index=0 if st.session_state.model == "claude-haiku-4-5-20251001" else 1,
    )
    case_ids = data_loader.list_case_ids(case_bank)
    selected_id = st.selectbox("증례 선택", case_ids)

    if st.button("진료 시작 (초기화)"):
        st.session_state.case = data_loader.get_case(case_bank, selected_id)
        st.session_state.chat_log = []
        st.session_state.exam_log = []
        st.session_state.diagnosis_form = None
        st.session_state.grading_result = None
        st.rerun()

st.title("🩺 CPX LLM — 복통 환자 역할극 & 자동 채점 (Streamlit)")

if st.session_state.case is None:
    st.info("왼쪽에서 API 키와 증례를 선택하고 '진료 시작'을 누르세요.")
    st.stop()

case = st.session_state.case
st.caption(f"주소: {case['chief_complaint']} · 환자: {case['patient']['name']}({case['patient']['age']}{case['patient']['sex']})")

col_exam, col_chat = st.columns([1, 2])

with col_exam:
    exam_panel.render_exam_panel(case)  # 개발자 B 작업물

with col_chat:
    patient_chat.render_chat(st.session_state.chat_log)
    doctor_text = st.chat_input("질문하거나 (행동) 형태로 진찰을 입력하세요")
    if doctor_text and st.session_state.api_key:
        patient_chat.append_doctor_message(doctor_text)  # 개발자 A 작업물
        st.rerun()
    elif doctor_text and not st.session_state.api_key:
        st.warning("API 키를 먼저 입력하세요.")

st.divider()

if st.session_state.grading_result is None:
    form_result = grading.render_diagnosis_form()  # 개발자 C 작업물
    if form_result:
        st.session_state.diagnosis_form = form_result
        with st.spinner("채점 중..."):
            st.session_state.grading_result = grading.call_grading(
                case, st.session_state.chat_log, form_result, st.session_state.api_key, st.session_state.model
            )
        st.rerun()
else:
    grading.render_dashboard(st.session_state.grading_result)  # 개발자 C 작업물
