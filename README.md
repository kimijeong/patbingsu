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

## 데이터/채점기준 수정 시 재생성 방법

증례 데이터(`data/case_bank.json`)나 채점 항목을 수정한 뒤에는 아래를 실행해 결과물을 재생성하세요.

```bash
cd scripts
python3 build_rubric.py      # rubric/CPX_채점기준표.xlsx 갱신
python3 build_chat_app.py    # index.html 갱신 (케이스/채점기준 재임베딩)
```

`build_rubric.py`로 수식이 포함된 엑셀을 다시 만들었다면, LibreOffice 기반 재계산 스크립트로 수식 오류 여부를 확인하는 것을 권장합니다 (Cowork 환경에서 사용한 `recalc.py`와 동일한 방식이며, 로컬에 LibreOffice가 설치되어 있다면 동일하게 사용 가능).

## 주의사항

- API 키는 본인이 직접 발급/결제하여 입력합니다. 이 프로젝트의 어떤 파일에도 실제 키가 저장되어 있지 않습니다.
- `index.html`은 Anthropic API에 브라우저에서 직접 요청합니다 (`anthropic-dangerous-direct-browser-access` 헤더 사용). 별도 서버가 필요 없습니다.
