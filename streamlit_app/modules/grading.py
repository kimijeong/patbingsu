"""
담당: 개발자 C
build_grading_prompt의 채점 기준 텍스트는 기존 index.html buildGradingPrompt()를 그대로 옮긴 것이니
내용은 바꾸지 말고(이미 검증됨) 출력 포맷(render_dashboard)만 자유롭게 다듬으면 됨.
render_dashboard는 방사형(radar) 차트까지 구현되어 있음 — 색/레이아웃 정도만 다듬으면 됨.
"""
from __future__ import annotations
import json
import streamlit as st
from anthropic import Anthropic
from . import data_loader

try:
    import plotly.graph_objects as go
except ImportError:
    go = None


def render_diagnosis_form() -> dict | None:
    st.subheader("진단서 작성")
    with st.form("diagnosis_form_ui"):
        impression = st.text_area("추정 진단명 (Impression)")
        tests = st.text_area("필요한 검사 목록 (Plan - Tests)")
        treatments = st.text_area("치료 및 교육 계획 (Plan - Treatments)")
        submitted = st.form_submit_button("진단서 최종 제출 및 채점")
    if submitted:
        return {"impression": impression, "tests": tests, "treatments": treatments}
    return None


def build_grading_prompt(case: dict, chat_log: list, diagnosis_form: dict) -> str:
    key = data_loader.get_key_items(case["case_id"])
    ak = case["answer_key"]
    transcript = "\n".join(
        f"{'[의사]' if m['role'] in ('doctor', 'exam') else '[환자]'} {m['text']}" for m in chat_log
    )
    treatments = ak.get("required_treatments") or ak.get("expected_skills", [])
    return f"""당신은 CPX 채점관입니다. 아래는 의대생(의사 역할)과 모의환자 챗봇 간의 대화 전체 기록과,
의대생이 작성한 최종 진단서입니다. 이를 근거로 100점 만점 채점표에 따라 채점하세요.

[증례: {case['case_id']} - {case['patient']['name']}({case['patient']['age']}{case['patient']['sex']}), 주증상: {case['chief_complaint']}]
[증례 핵심 포인트] 병력 핵심: {key['hx']} / 진찰 핵심: {key['pe']}
[정답 감별진단] {', '.join(ak['top_diagnoses'])}
[필요 검사] {', '.join(ak['required_tests'])}
[필요 치료/술기] {', '.join(treatments)}
[환자 질문] {case['patient_question']}

[채점 영역 및 배점]
1. 병력청취 40점: 핵심 감별 포인트 문진(8), OPQRST(5), 전신증상(4), 계통별 증상(4), 과거 유사병력/검진이력(4), 약물(4), 사회력(4), 가족력(4), 환자 질문 반영(3)
2. 신체진찰 20점: General/Vital(5), 기본 시/청/타/촉(5), 케이스 핵심 수기(5), 추가 진찰(5). ※촉진/타진은 대화/진찰신호에 구역이 구체적으로 명시되었는지로만 판단.
3. PPI 20점, 6항목(4/3/4/4/3/2): 효율적 문진·경청 / 생각·배경 파악 / 이해하기 쉬운 설명 / 유대관계 형성 / 체계적 진행 / 신체진찰 태도.
   ※손위생 등 텍스트로 확인 불가능한 비언어 항목은 명시적 언급이 없어도 대화 전반의 어투를 보고 관대하게 추정.
4. 임상추론 20점: 1순위 진단(6), 2~3순위 감별진단(3), 핵심검사 제안(6), 치료계획 언급(5). 진단서 내용을 최우선 근거로 평가.

[대화 기록]
{transcript}

[의대생이 작성한 진단서]
추정 진단명: {diagnosis_form['impression']}
필요한 검사: {diagnosis_form['tests']}
치료 및 교육 계획: {diagnosis_form['treatments']}

[출력 형식] 아래 JSON만 출력하세요. 다른 텍스트 없이 순수 JSON만.
{{
  "history_taking": {{"score": 0, "detail": ""}},
  "physical_exam": {{"score": 0, "detail": ""}},
  "ppi": {{"score": 0, "detail": ""}},
  "clinical_reasoning": {{"score": 0, "detail": ""}},
  "total": 0,
  "feedback": ""
}}"""


def call_grading(case: dict, chat_log: list, diagnosis_form: dict, api_key: str, model: str) -> dict:
    prompt = build_grading_prompt(case, chat_log, diagnosis_form)
    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=1200,
        system="당신은 정확하고 일관된 CPX 채점관입니다. 반드시 순수 JSON만 출력하세요.",
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(b.text for b in resp.content if hasattr(b, "text")).strip()
    raw = raw[raw.index("{"): raw.rindex("}") + 1]
    return json.loads(raw)


def render_dashboard(grading_result: dict) -> None:
    r = grading_result
    domains = ["history_taking", "physical_exam", "ppi", "clinical_reasoning"]
    labels = ["병력청취", "신체진찰", "PPI", "임상추론"]
    max_scores = [40, 20, 20, 20]
    scores = [r[d]["score"] for d in domains]
    pct = [round(s / m * 100, 1) for s, m in zip(scores, max_scores)]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("총점", f"{r['total']} / 100")
        for d, label, m in zip(domains, labels, max_scores):
            st.markdown(f"**{label}**: {r[d]['score']} / {m}")

    with col2:
        if go is not None:
            fig = go.Figure(
                go.Scatterpolar(
                    r=pct + [pct[0]],
                    theta=labels + [labels[0]],
                    fill="toself",
                    name="달성률(%)",
                )
            )
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("plotly가 설치되어 있지 않습니다. requirements.txt 기준으로 설치하세요.")

    st.divider()
    for d, label in zip(domains, labels):
        with st.expander(f"{label} 상세 — {r[d]['score']}점"):
            st.write(r[d]["detail"])

    st.markdown("### 피드백")
    st.write(r["feedback"])
