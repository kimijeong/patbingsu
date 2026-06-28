# CPX LLM — 복통 모의환자 시뮬레이터 & 자동 채점

복통(Abdominal Pain) 23개 증례를 기반으로 한 CPX(임상수행능력시험) 챗봇입니다. Claude API를 이용해
(1) 모의환자 역할극, (2) 대화 종료 후 채점기준표 기반 자동 채점/피드백을 제공합니다.

## 폴더 구조

```
codemedipotbingsu/
├── index.html              # 실행 파일 (브라우저에서 더블클릭으로 열기)
├── data/
│   └── case_bank.json       # 23개 증례 원본 데이터
├── rubric/
│   └── CPX_채점기준표.xlsx   # 채점기준표 (40/20/20/20점, 참고/문서용)
├── scripts/
│   ├── build_rubric.py      # case_bank.json → CPX_채점기준표.xlsx 생성
│   └── build_chat_app.py    # case_bank.json + 채점기준 → index.html 생성
└── README.md
```

## 사용법

1. `index.html`을 브라우저로 엽니다 (더블클릭, 서버 불필요).
2. 본인의 Anthropic API 키를 입력합니다 (https://console.anthropic.com 에서 발급).
   - 키는 브라우저 `localStorage`에만 저장되며 외부로 전송되지 않습니다.
   - 24시간 대량 테스트에는 **Claude Haiku 4.5**(기본값, 가장 저렴)를 추천합니다. 세션당 비용은 수십 원 단위로, 수백 회 테스트에도 부담이 적습니다. 품질을 높이려면 Sonnet 4.6으로 전환하세요.
3. 증례를 선택하고 "진료 시작"을 누릅니다.
4. 대화창에 입력:
   - 일반 텍스트 = 의사의 말 (문진)
   - `(괄호 텍스트)` = 의사의 신체진찰/행동 (예: `(우하복부를 깊게 눌러본다)`)
   - 촉진/타진은 부위(좌/우, 상/중/하 등)를 구체적으로 명시해야 정확한 소견을 받습니다.
5. 진료가 끝나면 "진료 종료 & 채점"을 누르면 LLM이 전체 대화를 바탕으로 100점 채점(병력청취 40 / 신체진찰 20 / PPI 20 / 임상추론 20)과 피드백을 제공합니다.

## 채점 정책 (중요)

- 손위생, 경청 자세 등 텍스트로 직접 확인이 불가능한 비언어적 PPI/진찰 태도 항목은, 명시적 언급이 없어도 대화 전반의 어투와 배려를 보고 **관대하게 추정**합니다.
- 촉진·타진 등 위치가 중요한 신체진찰 항목은 괄호 행동 텍스트에 **구역이 명시된 경우에만** 인정하는 엄격한 기준을 적용합니다.
- 이 정책은 `rubric/CPX_채점기준표.xlsx`의 "안내" 시트와 `index.html`의 채점 프롬프트에 동일하게 반영되어 있습니다.

## 데이터/채점기준 관리 — 단일 원본(Single Source of Truth)

증례 데이터와 채점기준의 **유일한 원본은 `data/case_bank.json`** 입니다. 각 증례 안에 환자
정보·병력·신체진찰 소견과 함께 `scoring` 블록(병력청취 체크리스트·예상 술기·필요검사·치료계획)이
들어 있습니다. 이 파일만 고치면 됩니다.

수정한 뒤에는 아래 한 줄만 실행하면 `index.html`(실제 앱)과 `rubric/CPX_채점기준표.xlsx`가 함께
동기화됩니다.

```bash
python3 scripts/sync_app.py
```

`sync_app.py`가 하는 일:

1. `index.html` 안의 `const CASE_BANK = {...}` / `const KEY_ITEMS = {...}` 데이터 블록만
   `case_bank.json` 기준으로 다시 채웁니다. (그 외 화면/로직/프롬프트/스타일은 건드리지 않음)
2. `KEY_ITEMS`(병력청취 체크리스트)는 각 증례의 `scoring.history_checklist` 에서 **자동 파생**되므로
   따로 관리할 필요가 없습니다.
3. `rubric/CPX_채점기준표.xlsx` 를 채점기준대로 새로 생성합니다(사람이 보는 참고 표).

> 참고: 실제 채점은 `index.html` 안에 임베드된 데이터로 동작합니다(더블클릭 실행 구조라 실행 중
> 외부 파일을 읽지 않음). 그래서 `case_bank.json` 수정 후에는 반드시 `sync_app.py` 를 실행해
> 앱에 반영해야 합니다.
>
> 구버전 `build_chat_app.py`/`build_rubric.py` 는 더 이상 사용하지 않습니다(옛 스키마용). 기존
> `data/case_bank_legacy.json` 은 이전 형식 백업본입니다.

## 주의사항

- API 키는 본인이 직접 발급/결제하여 입력합니다. 이 프로젝트의 어떤 파일에도 실제 키가 저장되어 있지 않습니다.
- `index.html`은 Anthropic API에 브라우저에서 직접 요청합니다 (`anthropic-dangerous-direct-browser-access` 헤더 사용). 별도 서버가 필요 없습니다.
