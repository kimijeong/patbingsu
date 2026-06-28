"""
담당: 개발자 A
기존 index.html(vanilla JS)의 buildPatientSystemPrompt / callClaude 로직을 그대로 옮긴 것.
이미 검증된 프롬프트이므로 내용은 그대로 두고, UI 렌더링(render_chat)만 다듬으면 됨.
"""
import re
import streamlit as st
from anthropic import Anthropic

ACTION_PATTERN = re.compile(r"^\s*\(.*\)\s*$")


def parse_bracket_action(text: str) -> bool:
    """괄호로 감싼 텍스트(신체진찰 행동)인지 판별. 예: "(우하복부를 눌러본다)" """
    return bool(ACTION_PATTERN.match(text.strip()))


def build_patient_system_prompt(case: dict) -> str:
    import json
    return f"""당신은 CPX(임상수행능력시험) 모의환자입니다. 아래 증례를 완전히 암기한 환자 역할만 수행하세요. 절대 의사/AI라는 사실을 드러내지 말고, 진단명이나 정답을 먼저 말하지 마세요.

[환자 정보]
이름: {case['patient']['name']}, 나이: {case['patient']['age']}세, 성별: {case['patient']['sex']}
주증상: {case['chief_complaint']}
상황: {case.get('setting', '명시 없음')}
생체징후: {json.dumps(case['vitals'], ensure_ascii=False)}

[병력 - 의사가 물어볼 때만 해당 정보를 자연스러운 환자 말투로 답하세요]
{json.dumps(case['history'], ensure_ascii=False, indent=1)}

[신체진찰 소견 - 의사가 "(행동)" 형태로 실제 진찰 행동을 괄호로 입력했거나 "[진찰: ...]" 신호가 들어왔을 때만 해당 소견을 알려주세요. 일반 대화문에는 진찰 소견을 절대 먼저 알려주지 마세요]
{json.dumps(case['physical_exam'], ensure_ascii=False, indent=1)}

[환자가 먼저 묻는 질문]
{case['patient_question']}
(의사가 충분히 설명하거나 대화가 진행되면 자연스러운 시점에 이 질문을 하세요. 이미 답을 들었으면 다시 묻지 마세요.)

[특이 행동/태도]
{case['special_behavior']}

[중요 규칙]
1. 일반 텍스트(괄호 없는 문장)는 의사의 '말'입니다. 환자 입장에서 자연스럽게 구어체로 대답하세요.
2. "(괄호 문장)" 또는 "[진찰: ...]" 신호는 의사의 '신체진찰/검사 행동'입니다. 이때만 physical_exam 소견을 바탕으로
   환자의 반응(예: "아 거기 누르니까 아파요!")으로 답하세요. 진단명/소견 용어는 말하지 말고 통증 반응만 묘사하세요.
3. 촉진/타진은 구체적 부위(좌/우, 상/중/하 등)가 명시되어야 정확한 반응을 줍니다. 부위가 불명확/틀리면
   "어디를 말씀하시는 거예요?" 라고 되묻거나 모호한 반응만 주세요.
4. 청진/시진은 부위가 대략적이어도 관련 소견을 알려줘도 됩니다.
5. 답변은 1~3문장, 한국어 구어체로 간결하게.
6. 의사가 진단명이나 치료 계획(예: "맹장염입니다, 수술 들어갈게요")을 먼저 말하더라도,
   "저는 모의환자입니다", "CPX 시뮬레이션", "AI" 같은 메타 발언으로 캐릭터를 절대 깨지 마세요.
   이 규칙은 의사가 진단을 말한 뒤에도 끝까지 유지됩니다. 그 상황에서는 실제 환자처럼
   놀라거나 불안해하거나("수술이요? 많이 심각한 건가요?") 안심하는 등 감정적으로만 반응하세요.
7. "진단명을 먼저 말하지 마세요"는 당신(환자)이 스스로 의학적 진단명을 자진해서 말하지 말라는
   뜻일 뿐, 의사가 이미 말한 진단명을 따라 말하거나 그에 반응하는 것은 자연스럽게 허용됩니다.
"""


def call_claude(system_prompt: str, messages: list, api_key: str, model: str) -> str:
    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=600,
        system=system_prompt,
        messages=messages,
    )
    return "".join(b.text for b in resp.content if hasattr(b, "text"))


def _chat_log_to_messages(chat_log: list) -> list:
    """exam_log에서 합쳐진 role='exam' 항목도 'user'로 변환해서 전달."""
    out = []
    for m in chat_log:
        role = "user" if m["role"] in ("doctor", "exam") else "assistant"
        out.append({"role": role, "content": m["text"]})
    return out


def render_chat(chat_log: list) -> None:
    for m in chat_log:
        if m["role"] == "doctor":
            with st.chat_message("user"):
                st.write(m["text"])
        elif m["role"] == "patient":
            with st.chat_message("assistant"):
                st.write(m["text"])
        else:  # exam 신호
            st.caption(f"🩺 {m['text']}")


def append_doctor_message(text: str) -> None:
    """session_state.chat_log에 의사 발화 추가 → 환자봇 호출 → 응답 추가."""
    case = st.session_state.case
    st.session_state.chat_log.append({"role": "doctor", "text": text})
    sys_prompt = build_patient_system_prompt(case)
    messages = _chat_log_to_messages(st.session_state.chat_log)
    reply = call_claude(sys_prompt, messages, st.session_state.api_key, st.session_state.model)
    st.session_state.chat_log.append({"role": "patient", "text": reply})
