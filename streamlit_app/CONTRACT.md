# 팀 작업 공통 인터페이스 (먼저 읽고 합의할 것)

3명이 동시에 작업해도 충돌 안 나게 하려면, 아래 "계약"만 지키면 됩니다.
각자 자기 모듈 안의 구현 디테일은 자유롯게 바꿔도 되지만, **함수 이름/입출력 형태와
session_state 키 이름은 여기 정의된 대로 고정**합니다. 바꿔야 하면 셋이 합의 후 이 파일을 수정하세요.

## 담당 분배

| 모듈 | 파일 | 담당 (정해서 적기) | Gemini 로드맵 단계 |
|---|---|---|---|
| 데이터 로더 | `modules/data_loader.py` | 개발자 A (코어, 제일 먼저 끝내야 함) | 1단계 |
| 환자봇 채팅 | `modules/patient_chat.py` | 개발자 A 또는 공동 | 1~2단계 |
| 진찰 패널 (4분할+괄호) | `modules/exam_panel.py` | 개발자 B | 3단계 |
| 진단서+채점+대시보드 | `modules/grading.py` | 개발자 C | 4~5단계 |
| 메인 레이아웃 | `app.py` | 다같이(처음 골격만), 이후 머지 담당자 1명 | - |

## 1. session_state 스키마 (전원 동일하게 사용)

```python
st.session_state.case            # dict, 현재 선택된 케이스 전체 (data_loader.get_case 결과)
st.session_state.chat_log        # list[dict], [{"role": "doctor"|"patient"|"exam", "text": str}]
st.session_state.exam_log        # list[dict], [{"zone": "RUQ"|"LUQ"|"RLQ"|"LLQ", "action": "압통"|"반발통"|"특수진찰", "note": str}]
st.session_state.diagnosis_form  # dict | None, {"impression": str, "tests": str, "treatments": str}
st.session_state.grading_result  # dict | None, build_grading_prompt 결과를 파싱한 채점 JSON
st.session_state.api_key         # str, 사용자가 입력 (파일에 저장하지 않음)
st.session_state.model           # str, 기본값 "claude-haiku-4-5-20251001"
```

`chat_log`의 `role="exam"` 항목은 4분할 버튼 클릭으로 생성된 시스템 신호용입니다.
예: `{"role": "exam", "text": "[진찰: 우상복부 압통 확인]"}` — 이 항목도 환자봇 API 호출 시
대화 맥락(messages)에 포함시켜서 환자봇이 반응하게 합니다 (role은 'user'로 변환해서 전달).

## 2. 함수 시그니처

### `modules/data_loader.py`
```python
def load_case_bank(path: str = "../data/case_bank.json") -> dict: ...
def list_case_ids(case_bank: dict) -> list[str]: ...
def get_case(case_bank: dict, case_id: str) -> dict: ...       # 케이스 1건 dict 반환
def get_key_items(case_id: str) -> dict: ...                    # {"hx": str, "pe": str} 반환
```
반환되는 case dict 구조 (`data/case_bank.json` 그대로):
`case_id, category, patient{name,age,sex}, chief_complaint, setting, vitals, history,
physical_exam, patient_question, special_behavior, answer_key{top_diagnoses, required_tests,
required_treatments, expected_skills}`

### `modules/patient_chat.py`
```python
def build_patient_system_prompt(case: dict) -> str: ...
def call_claude(system_prompt: str, messages: list[dict], api_key: str, model: str) -> str: ...
def render_chat(chat_log: list[dict]) -> None: ...               # st.chat_message로 렌더링
def append_doctor_message(text: str) -> None: ...                # session_state.chat_log에 추가 + call_claude 호출 + 응답 추가
def parse_bracket_action(text: str) -> bool: ...                  # "(...)" 패턴이면 True
```

### `modules/exam_panel.py`
```python
def render_exam_panel(case: dict) -> None: ...   # 2x2 그리드(우상/좌상/우하/좌하) + 압통/반발통/특수진찰 서브 선택
def on_exam_action(zone: str, action: str) -> None: ...  # exam_log에 추가 + chat_log에 "[진찰: ...]" 추가 + patient_chat 호출
```

### `modules/grading.py`
```python
def render_diagnosis_form() -> dict | None: ...   # 3개 입력 필드, 제출 시 dict 반환, 아니면 None
def build_grading_prompt(case: dict, chat_log: list[dict], diagnosis_form: dict) -> str: ...
def call_grading(case: dict, chat_log: list[dict], diagnosis_form: dict, api_key: str, model: str) -> dict: ...
def render_dashboard(grading_result: dict) -> None: ...  # 총점 metric + plotly 방사형/바 차트 + 마크다운 피드백
```
`grading_result` JSON 스키마 (기존 index.html 채점 프롬프트와 동일하게 유지):
```json
{
  "history_taking": {"score": 0, "detail": ""},
  "physical_exam": {"score": 0, "detail": ""},
  "ppi": {"score": 0, "detail": ""},
  "clinical_reasoning": {"score": 0, "detail": ""},
  "total": 0,
  "feedback": ""
}
```

## 3. 작업 순서 (필수)

1. **오늘**: 위 스키마/시그니처에 이상 없는지 셋이 5분 합의. 이름 바꾸고 싶으면 지금 바꾸고 시작.
2. **acute_01 케이스 하나만**으로 끝까지 파이프라인 연결 (33개 다 테스트하지 말 것).
3. 각자 모듈은 다른 두 명이 안 끝나도 mock 데이터로 독립 개발 가능
   (예: 개발자 B는 `case_bank.json`의 acute_01 physical_exam 부분만 보고 4분할 UI 먼저 만들면 됨,
   개발자 A의 patient_chat 완성을 기다릴 필요 없음).
4. 거의 매일 git merge로 통합, app.py에서 합쳐서 실제 동작 확인.
5. acute_01 파이프라인이 끝까지 뚫리면 나머지 22개 케이스는 데이터 구조가 같아서 자동으로 동작.

## 4. 참고 - 이미 만들어진 재사용 자산

- `data/case_bank.json` — 23개 증례 원본 (그대로 재사용)
- `rubric/CPX_채점기준표.xlsx` — 채점 배점/항목 원본 문서
- 기존 `index.html` (서버 없는 vanilla JS 버전) — 환자봇 시스템 프롬프트, 채점 프롬프트, KEY_ITEMS(케이스별 핵심 포인트) 로직을 그대로 가져다 쓰면 됨. `modules/patient_chat.py`와 `modules/grading.py`의 프롬프트 빌딩 함수는 index.html 안의 `buildPatientSystemPrompt`, `buildGradingPrompt`를 파이썬으로 옮기면 됨 (로직 동일, 이미 검증된 프롬프트).
