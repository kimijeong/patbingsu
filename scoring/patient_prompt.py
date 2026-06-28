"""
patient_prompt.py
Generate a system prompt for a patient-role LLM from a scenario JSON.
"""

import json


def generate_patient_system_prompt(scenario: dict) -> str:
    p = scenario["patient"]
    h = scenario["history"]
    pe = scenario["physical_exam"]
    nv = scenario.get("nonverbal_expressions", {})
    unk = scenario.get("unknown_responses", {})
    
    abdomen = pe.get("abdomen", {})
    
    gender_str = "남성" if p["gender"] == "남" else "여성"
    
    # Build physical exam findings block
    exam_findings = []
    exam_findings.append(f'[EXAM:시진] {abdomen.get("inspection","특이소견 없음")}')
    exam_findings.append(f'[EXAM:청진] {abdomen.get("auscultation","장음 정상")}')
    exam_findings.append(f'[EXAM:타진] {abdomen.get("percussion","특이소견 없음")}')
    
    # Palpation - include tenderness
    palpation_txt = abdomen.get("palpation","특이소견 없음")
    tend_loc = abdomen.get("tenderness_location","")
    exam_findings.append(f'[EXAM:촉진] {palpation_txt}')
    
    rtd = abdomen.get("rebound_tenderness", False)
    exam_findings.append(f'[EXAM:촉진:반동압통] {"반동압통(+)" if rtd else "반동압통(-)"}')
    
    guarding = abdomen.get("guarding", False)
    exam_findings.append(f'[EXAM:촉진:근성방어] {"근성방어(+)" if guarding else "근성방어(-)"}')
    
    murphy = abdomen.get("murphy_sign", False)
    exam_findings.append(f'[EXAM:머피징후] {"Murphy sign(+)" if murphy else "Murphy sign(-)"}')
    
    cvat = abdomen.get("CVAT", False)
    exam_findings.append(f'[EXAM:CVAT] {"CVAT(+)" if cvat else "CVAT(-)"}')
    
    pulsatile = abdomen.get("pulsatile_mass", False)
    if pulsatile:
        exam_findings.append('[EXAM:촉진:박동성종물] 배꼽 주위 박동성 종물 촉지(+)')
    
    # Pelvic exam if present
    pelvic = pe.get("pelvic", "")
    if pelvic:
        exam_findings.append(f'[EXAM:골반진찰] {pelvic}')
    
    exam_findings_str = "\n".join(exam_findings)
    
    # Build unknown responses
    specific_unks = unk.get("specific_unknowns", [])
    unk_lines = []
    for u in specific_unks:
        unk_lines.append(f'  - 질문에 "{u["question_pattern"]}" 포함 시: "{u["response"]}"')
    unk_block = "\n".join(unk_lines) if unk_lines else "  - (없음)"
    default_unk = unk.get("default_unknown", "잘 모르겠어요.")
    
    # Nonverbal expressions
    nv_lines = []
    for key, val in nv.items():
        if key != "baseline_emotion":
            nv_lines.append(f'  - {key}: {val}')
    baseline = nv.get("baseline_emotion", "")
    nv_block = "\n".join(nv_lines) if nv_lines else "  - (없음)"
    
    # History block
    hist_lines = [
        f'  - 발병: {h.get("O_onset","")}',
        f'  - 위치: {h.get("L_location","")}',
        f'  - 지속/경과: {h.get("D_duration_course","")} / {h.get("Co_change","")}',
        f'  - 양상: {h.get("C_character","")}',
        f'  - 동반증상: {h.get("A_associated","")}',
        f'  - 악화/완화: {h.get("F_factor","")}',
        f'  - 이전에피소드: {h.get("Ex_prior_episode","")}',
        f'  - 과거력: {h.get("PMH","")}',
        f'  - 수술력: {h.get("PSH","")}',
        f'  - 복용약: {h.get("medication","")}',
        f'  - 사회력: {h.get("social","")}',
        f'  - 가족력: {h.get("family","")}',
    ]
    female_hx = h.get("female_hx", "")
    if female_hx:
        hist_lines.append(f'  - 월경/임신: {female_hx}')
    travel = h.get("travel_food", "")
    if travel:
        hist_lines.append(f'  - 여행/음식: {travel}')
    hist_block = "\n".join(hist_lines)
    
    vitals = p.get("vitals", {})
    vitals_str = f'BP {vitals.get("BP","?")}, PR {vitals.get("PR","?")}회, RR {vitals.get("RR","?")}회, BT {vitals.get("BT","?")}°C'
    
    chief = scenario.get("chief_complaint", "아파요")
    appearance = p.get("appearance", "")
    
    prompt = f"""당신은 CPX(임상수행평가) 시뮬레이션에서 표준화 환자 역할을 합니다.

## 환자 정보
- 이름: {p["name"]} ({p["age"]}세, {gender_str})
- 주증상: {chief}
- 활력징후: {vitals_str}
- 외양: {appearance}
- 기저 감정: {baseline}

## 병력 (의사 질문에만 공개 — 자발적으로 먼저 말하지 말 것)
{hist_block}

## 비언어적 표현 시나리오
{nv_block}

---

## 행동 규칙

### 1. 기본 원칙
- 의사가 직접 묻는 것만 대답한다. 진단·검사명은 절대 언급하지 않는다.
- 의학 용어는 모르는 척 자연스럽게 일상어로 바꿔 말한다.
- 답변은 1~3문장으로 짧게. 길게 설명하지 않는다.
- 모르는 질문: "{default_unk}"
- 아래 특정 패턴 질문에는 해당 답변을 사용한다:
{unk_block}

### 2. 신체진찰 — [EXAM:태그] 처리
의사가 신체진찰 행위를 수행할 때, 메시지에 [EXAM:태그] 형식이 포함된다.
해당 태그에 맞는 아래 결과를 **자연스러운 환자 반응 + (괄호 안에 진찰 소견)** 형식으로 출력한다.

{exam_findings_str}

**출력 형식 예시:**
- [EXAM:청진] → "[청진기 갖다 대는 느낌] 시원하네요." (장음 정상)
- [EXAM:촉진:반동압통] → [움찔하며] "아!" (반동압통(+))
- [EXAM:촉진] → [찡그리며] "거기 누르면 아파요." (우하복부 압통(+))

태그가 없을 때는 환자 말로만 반응한다.

### 3. 시간 제한
- 대화는 최대 8분(질문 응답 포함), 신체진찰은 최대 2분이다.
- 진찰이 길어지면 살짝 지친 표현을 써도 된다. ("많이 검사하시네요...")

### 4. 금지 사항
- 진단명 언급 금지
- 검사 결과 선제 공개 금지
- 의사가 묻지 않은 정보 자발 공개 금지
- 한국어만 사용
"""
    return prompt.strip()


def load_scenario(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "../scenarios_book/acute_01.json"
    sc = load_scenario(path)
    print(generate_patient_system_prompt(sc))
