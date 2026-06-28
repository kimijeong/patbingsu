import json

cb = json.load(open("../data/case_bank.json", encoding="utf-8"))

KEY = {
 "acute_01": {"hx":"임신 가능성/LMP 확인, 통증 이동 양상(배꼽주변→우하복부), 방사통 여부 문진","pe":"Psoas sign/Obturator sign 시행"},
 "acute_02": {"hx":"기름진 음식/과식과의 연관성, 황달·소변색·가려움 문진","pe":"Murphy's sign 시행"},
 "acute_03": {"hx":"체중감소·지방변·다음/다뇨/다갈 등 췌장기능 관련 문진, 음주력 확인","pe":"DRE 시행"},
 "acute_04": {"hx":"통증 양상(칼로 찢는 듯)과 자세에 따른 변화, 음주력 확인","pe":"DRE 및 복막자극징후 확인"},
 "acute_05": {"hx":"황달/가려움/소변색·대변색 변화 문진","pe":"결막 황달 확인, DRE"},
 "acute_06": {"hx":"임신 가능성/생리 관련 부인과 문진, 통증 이동 양상 확인","pe":"Rovsing/Psoas/Obturator sign 시행"},
 "acute_07": {"hx":"혈뇨/배뇨통 등 비뇨기 증상, 콜릭성 통증 양상 확인","pe":"CVA tenderness 확인"},
 "chronic_01": {"hx":"체중감소 및 식전/공복 시 악화 양상(궤양 시사) 확인","pe":"Epigastric tenderness 확인"},
 "chronic_02": {"hx":"가족력(췌장염/담낭암)과 음주력 확인","pe":"Murphy's sign, CVAT 확인"},
 "chronic_03": {"hx":"체중감소 정도와 경고증상(red flag) 확인","pe":"복부 압통 여부 정밀 확인"},
 "chronic_04": {"hx":"체중감소 및 식후 패턴, 당뇨 조절 상태 확인","pe":"반동압통(rebound tenderness) 여부 명확히 확인"},
 "chronic_05": {"hx":"배변과의 연관성, 스트레스 요인(자녀 문제 등) 확인","pe":"복부 촉진 및 골반 내진"},
 "chronic_06": {"hx":"스트레스/식습관 및 경고증상(체중감소 등) 부재 확인","pe":"Epigastric tenderness 확인"},
 "chronic_07": {"hx":"복용 약물(항생제/소염제 등) 구체적 확인","pe":"DRE 시행(혈변 감별)"},
 "chronic_08": {"hx":"당뇨 조절 상태(HbA1c, 약물 순응도) 확인","pe":"DRE 시행"},
 "acute_08": {"hx":"임신 가능성/LMP 확인, 질출혈 양상, 어지럼/실신감 등 쇼크 징후 문진","pe":"골반 내진 및 자궁목 유동 압통(CMT) 확인"},
 "acute_09": {"hx":"복부 수술력(PSH), 가스 배출/배변 여부 확인","pe":"복부 시진(팽만/수술흉터) 및 청진(금속성 장음) 확인"},
 "acute_10": {"hx":"혈뇨/배뇨통 등 비뇨기 증상과 콜릭성 통증 양상 확인","pe":"CVA tenderness 확인"},
 "acute_11": {"hx":"기름진 음식과의 연관성 및 통증 지속시간(1~5시간) 확인","pe":"Murphy's sign 및 황달 확인"},
 "extra_01": {"hx":"공동 식사자 등 역학적 노출력 확인","pe":"탈수 소견(피부긴장도/구강점막) 평가"},
 "extra_02": {"hx":"성생활력/성매개감염 위험요인 확인, 임신 가능성 배제","pe":"골반 내진(자궁목 유동압통, 부속기 압통) 확인"},
 "extra_03": {"hx":"NSAID/항응고제 복용력, 토혈/흑색변 여부 확인","pe":"직장수지검사(흑색변) 및 기립성 저혈압 등 쇼크 징후 확인"},
 "extra_04": {"hx":"심혈관 위험요인(당뇨/고혈압/흡연/가족력) 및 방사통(어깨/턱) 확인","pe":"심전도 우선 고려 및 발한 등 전신소견 확인"},
}

CASES_JSON = json.dumps(cb, ensure_ascii=False)
KEY_JSON = json.dumps(KEY, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CPX LLM - 복통 시뮬레이터</title>
<style>
  :root {
    --blue: #4472C4; --green: #2e7d32; --bg: #f4f6fb; --card: #ffffff;
    --border: #d8dee9; --text: #1f2733; --muted: #667085;
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    background: var(--bg); color: var(--text); margin: 0; padding: 16px;
  }
  .wrap { max-width: 980px; margin: 0 auto; }
  h1 { font-size: 20px; margin: 4px 0 14px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 14px; }
  .row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
  label { font-size: 13px; color: var(--muted); margin-bottom: 4px; display: block; }
  select, input[type=text], input[type=password] {
    padding: 8px 10px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; width: 100%;
  }
  button {
    background: var(--blue); color: #fff; border: none; border-radius: 6px;
    padding: 9px 16px; font-size: 14px; cursor: pointer;
  }
  button.secondary { background: #fff; color: var(--blue); border: 1px solid var(--blue); }
  button:disabled { opacity: .5; cursor: not-allowed; }
  .field { flex: 1; min-width: 160px; }
  .hint { font-size: 12px; color: var(--muted); margin-top: 6px; line-height: 1.5; }
  #chat {
    height: 420px; overflow-y: auto; border: 1px solid var(--border); border-radius: 8px;
    padding: 12px; background: #fafbfd; display: flex; flex-direction: column; gap: 10px;
  }
  .msg { max-width: 80%; padding: 9px 12px; border-radius: 10px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
  .msg.doctor { align-self: flex-end; background: var(--blue); color: #fff; }
  .msg.patient { align-self: flex-start; background: #e9edf3; color: var(--text); }
  .msg.action { font-style: italic; opacity: .85; }
  .msg.system { align-self: center; background: #fff3cd; color: #7a5b00; font-size: 12px; }
  .inputbar { display: flex; gap: 8px; margin-top: 10px; }
  .inputbar input { flex: 1; }
  .tag { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #eef1f6; color: var(--muted); margin-right: 6px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { border: 1px solid var(--border); padding: 6px 8px; text-align: left; vertical-align: top; }
  th { background: #eef1f6; }
  .score-total { font-size: 28px; font-weight: 700; color: var(--blue); }
  .domain-bar { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 12px; }
  .domain-pill { background: #eef1f6; border-radius: 8px; padding: 8px 12px; font-size: 13px; }
  .domain-pill b { color: var(--blue); }
  #grading-result { display: none; }
  .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid #cdd6e3; border-top-color: var(--blue); border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 6px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .small { font-size: 12px; color: var(--muted); }
</style>
</head>
<body>
<div class="wrap">
  <h1>🩺 CPX LLM — 복통 환자 역할극 &amp; 자동 채점</h1>

  <div class="card">
    <div class="row">
      <div class="field">
        <label>Anthropic API 키 (브라우저에만 저장, 본인 컴퓨터 외 전송되지 않음)</label>
        <input type="password" id="apiKey" placeholder="sk-ant-...">
      </div>
      <div class="field" style="max-width:220px;">
        <label>모델</label>
        <select id="modelSelect">
          <option value="claude-haiku-4-5-20251001">Claude Haiku 4.5 (저비용, 대량 테스트 추천)</option>
          <option value="claude-sonnet-4-6">Claude Sonnet 4.6 (고품질, 비용 ↑)</option>
        </select>
      </div>
    </div>
    <div class="hint">
      API 키는 <b>localStorage</b>에만 저장되어 본인 브라우저를 벗어나지 않습니다. 24시간 대량 테스트에는 Haiku 4.5가 토큰당 1/3~1/5 가격으로 충분히 좋은 역할극 품질을 냅니다.
    </div>
  </div>

  <div class="card">
    <div class="row">
      <div class="field">
        <label>증례 선택 (23개)</label>
        <select id="caseSelect"></select>
      </div>
      <button id="startBtn">진료 시작</button>
      <button id="endBtn" class="secondary" disabled>진료 종료 &amp; 채점</button>
    </div>
    <div class="hint" id="caseInfo"></div>
  </div>

  <div class="card">
    <div id="chat"></div>
    <div class="inputbar">
      <input type="text" id="userInput" placeholder="대화는 그대로 입력, 신체진찰/행동은 (예: 우하복부를 눌러본다) 처럼 괄호로 입력하세요." disabled>
      <button id="sendBtn" disabled>전송</button>
    </div>
    <div class="hint">
      예시 — 문진: <code>언제부터 아프셨어요?</code> / 진찰 행동: <code>(우측 하복부를 깊게 눌러본다)</code>, <code>(청진기를 배에 댄다)</code>.
      촉진·타진은 좌/우, 상/중/하 등 <b>구역을 구체적으로 명시</b>해야 인정됩니다.
    </div>
  </div>

  <div class="card" id="grading-result">
    <h2>채점 결과</h2>
    <div id="gradingBody"></div>
  </div>
</div>

<script>
const CASES = __CASES_JSON__;
const KEY_ITEMS = __KEY_JSON__;

const caseSelect = document.getElementById('caseSelect');
const caseInfo = document.getElementById('caseInfo');
const chatEl = document.getElementById('chat');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const startBtn = document.getElementById('startBtn');
const endBtn = document.getElementById('endBtn');
const apiKeyEl = document.getElementById('apiKey');
const modelSelect = document.getElementById('modelSelect');
const gradingResult = document.getElementById('grading-result');
const gradingBody = document.getElementById('gradingBody');

apiKeyEl.value = localStorage.getItem('cpx_api_key') || '';
apiKeyEl.addEventListener('change', () => localStorage.setItem('cpx_api_key', apiKeyEl.value));
if (localStorage.getItem('cpx_model')) modelSelect.value = localStorage.getItem('cpx_model');
modelSelect.addEventListener('change', () => localStorage.setItem('cpx_model', modelSelect.value));

CASES.cases.forEach((c, i) => {
  const opt = document.createElement('option');
  opt.value = i;
  opt.textContent = `[${c.case_id}] ${c.category} - ${c.patient.name}(${c.patient.age}${c.patient.sex})`;
  caseSelect.appendChild(opt);
});

let currentCase = null;
let transcript = []; // {role: 'doctor'|'patient', text}

function renderCaseInfo() {
  const c = currentCase;
  caseInfo.innerHTML = `주소: ${c.chief_complaint} · 환자질문: ${c.patient_question} · 세팅: ${c.setting || '-'}`;
}

function addMsg(role, text) {
  const div = document.createElement('div');
  const isAction = /^\\s*\\(.*\\)\\s*$/.test(text.trim());
  div.className = 'msg ' + role + (isAction ? ' action' : '');
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function addSystemMsg(text) {
  const div = document.createElement('div');
  div.className = 'msg system';
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function buildPatientSystemPrompt(c) {
  return `당신은 CPX(임상수행능력시험) 모의환자입니다. 아래 증례를 완전히 암기한 환자 역할만 수행하세요. 절대 의사/AI라는 사실을 드러내지 말고, 진단명이나 정답을 먼저 말하지 마세요.

[환자 정보]
이름: ${c.patient.name}, 나이: ${c.patient.age}세, 성별: ${c.patient.sex}
주증상: ${c.chief_complaint}
상황: ${c.setting || '명시 없음'}
생체징후: ${JSON.stringify(c.vitals)}

[병력 - 의사가 물어볼 때만 해당 정보를 자연스러운 환자 말투로 답하세요]
${JSON.stringify(c.history, null, 1)}

[신체진찰 소견 - 의사가 "(행동)" 형태로 실제 진찰 행동을 괄호로 입력했을 때만 해당 소견을 알려주세요. 일반 대화문에는 진찰 소견을 절대 먼저 알려주지 마세요]
${JSON.stringify(c.physical_exam, null, 1)}

[환자가 먼저 묻는 질문]
${c.patient_question}
(의사가 충분히 설명하거나 대화가 진행되면 자연스러운 시점에 이 질문을 하세요. 이미 답을 들었으면 다시 묻지 마세요.)

[특이 행동/태도]
${c.special_behavior}

[중요 규칙]
1. 일반 텍스트(괄호 없는 문장)는 의사의 '말'입니다. 환자 입장에서 자연스럽게 구어체로 대답하세요. 의학 용어 대신 일상 표현을 쓰세요.
2. "(괄호로 감싼 문장)"은 의사의 '신체진찰/검사 행동'입니다. 이때만 physical_exam 소견을 바탕으로 환자의 반응(예: "아 거기 누르니까 아파요!", "괜찮아요, 안 아파요")으로 답하세요. 진단명이나 소견 용어(예: "Murphy's sign 양성")는 절대 말하지 말고 통증 반응만 묘사하세요.
3. 촉진(누르다)/타진(두드리다)은 의사가 구체적 부위(좌/우, 상/중/하 등)를 명시해야 정확한 반응을 줍니다. 부위가 불명확하거나 틀린 부위면 "어디를 말씀하시는 거예요?" 라고 되묻거나 미세한/모호한 반응만 주고, 핵심 소견(예: McBurney's point tenderness)은 정확한 부위를 짚었을 때만 드러내세요.
4. 청진/시진은 부위가 대략적이어도(예: "(배에 청진기를 댄다)") 관련 소견을 알려줘도 됩니다.
5. 의사가 진단/검사/치료를 설명하면 일반인 입장에서 반응하세요(겁먹거나 안심하거나 등, special_behavior 참고).
6. 답변은 1~3문장 내로 간결하게, 한국어 구어체로 하세요.
7. 의사가 진단명이나 치료 계획(예: "맹장염입니다, 수술 들어갈게요")을 먼저 말하더라도, "저는 모의환자입니다", "CPX 시뮬레이션", "AI" 같은 메타 발언으로 캐릭터를 절대 깨지 마세요. 이 규칙은 의사가 진단을 말한 뒤에도 끝까지 유지됩니다. 그 상황에서는 실제 환자처럼 놀라거나 불안해하거나("수술이요? 많이 심각한 건가요?") 안심하는 등 감정적으로만 반응하세요.
8. "진단명을 먼저 말하지 마세요"는 당신(환자)이 스스로 의학적 진단명을 자진해서 말하지 말라는 뜻일 뿐, 의사가 이미 말한 진단명을 따라 말하거나 그에 반응하는 것은 자연스럽게 허용됩니다.`;
}

function buildGradingPrompt(c, transcriptText) {
  const k = KEY_ITEMS[c.case_id];
  const ak = c.answer_key;
  return `당신은 CPX 채점관입니다. 아래는 의대생(의사 역할)과 모의환자 챗봇 간의 대화 전체 기록입니다. 이 대화만을 근거로 100점 만점 채점표에 따라 채점하세요.

[증례: ${c.case_id} - ${c.patient.name}(${c.patient.age}${c.patient.sex}), 주증상: ${c.chief_complaint}]
[증례 핵심 포인트] 병력 핵심: ${k.hx} / 진찰 핵심: ${k.pe}
[정답 감별진단] ${ak.top_diagnoses.join(', ')}
[필요 검사] ${ak.required_tests.join(', ')}
[필요 치료/술기] ${(ak.required_treatments.length?ak.required_treatments:ak.expected_skills).join(', ')}
[환자 질문] ${c.patient_question}

[채점 영역 및 배점]
1. 병력청취 40점: 핵심 감별 포인트 문진(8), OPQRST(5), 전신증상(4), 계통별 증상(4), 과거 유사병력/검진이력(4), 약물(4), 사회력(4), 가족력${c.patient.sex==='여'?'/여성력':''}(4), 환자 질문 반영(3)
2. 신체진찰 20점: General/Vital(5), 기본 시/청/타/촉(5), 케이스 핵심 수기(5), 추가 진찰(DRE/골반 등, 5). ※촉진/타진은 대화 중 '(괄호 행동)'으로 구역을 구체적으로 명시했는지 텍스트 근거로만 판단. 명시 없으면 미시행으로 채점.
3. PPI(환자-의사관계) 20점, 6항목 — 4/3/4/4/3/2: (1)효율적 문진·경청(4) (2)생각/배경 파악(3) (3)이해하기 쉬운 설명(4) (4)유대관계 형성(4) (5)체계적 진행(3) (6)신체진찰 태도(2). ※손위생/가려주기처럼 텍스트로 확인 불가능한 비언어 항목은 명시적 언급이 없어도 대화 전반의 어투·배려를 보고 관대하게(보통 이상 기본값) 추정.
4. 임상추론 20점: 1순위 진단 언급(6), 2~3순위 감별진단 언급(3), 핵심검사 제안(6), 치료계획/술기 언급(5)

[대화 기록]
${transcriptText}

[출력 형식] 아래 JSON만 출력하세요. 다른 텍스트 없이 순수 JSON만.
{
  "history_taking": {"score": 0-40, "detail": "항목별 평가 요약"},
  "physical_exam": {"score": 0-20, "detail": "항목별 평가 요약, 구역 명시 여부 포함"},
  "ppi": {"score": 0-20, "detail": "6항목 각각 점수와 근거"},
  "clinical_reasoning": {"score": 0-20, "detail": "진단/검사/치료 언급 평가"},
  "total": 0-100,
  "feedback": "전반적 피드백 2~4문장, 잘한 점과 개선점"
}`;
}

async function callClaude(systemPrompt, messages) {
  const apiKey = apiKeyEl.value.trim();
  if (!apiKey) { alert('API 키를 입력하세요.'); throw new Error('no key'); }
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true'
    },
    body: JSON.stringify({
      model: modelSelect.value,
      max_tokens: 600,
      system: systemPrompt,
      messages: messages
    })
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`API 오류 (${res.status}): ${errText}`);
  }
  const data = await res.json();
  return data.content.map(b => b.text || '').join('');
}

caseSelect.addEventListener('change', () => {});

startBtn.addEventListener('click', () => {
  const idx = parseInt(caseSelect.value || '0', 10);
  currentCase = CASES.cases[idx];
  transcript = [];
  chatEl.innerHTML = '';
  gradingResult.style.display = 'none';
  renderCaseInfo();
  addSystemMsg(`진료가 시작되었습니다. 환자: ${currentCase.patient.name}(${currentCase.patient.age}${currentCase.patient.sex}) — "${currentCase.chief_complaint}"`);
  userInput.disabled = false;
  sendBtn.disabled = false;
  endBtn.disabled = false;
  caseSelect.disabled = true;
  startBtn.disabled = true;
  userInput.focus();
});

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || !currentCase) return;
  addMsg('doctor', text);
  transcript.push({role: 'doctor', text});
  userInput.value = '';
  userInput.disabled = true;
  sendBtn.disabled = true;

  const sysPrompt = buildPatientSystemPrompt(currentCase);
  const msgs = transcript.map(t => ({
    role: t.role === 'doctor' ? 'user' : 'assistant',
    content: t.text
  }));

  try {
    const reply = await callClaude(sysPrompt, msgs);
    addMsg('patient', reply);
    transcript.push({role: 'patient', text: reply});
  } catch (e) {
    addSystemMsg('오류: ' + e.message);
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });

endBtn.addEventListener('click', async () => {
  if (!currentCase || transcript.length === 0) { alert('대화 내용이 없습니다.'); return; }
  userInput.disabled = true; sendBtn.disabled = true; endBtn.disabled = true;
  gradingResult.style.display = 'block';
  gradingBody.innerHTML = '<span class="spinner"></span>채점 중...';

  const transcriptText = transcript.map(t => `${t.role === 'doctor' ? '[의사]' : '[환자]'} ${t.text}`).join('\\n');
  const gradingPrompt = buildGradingPrompt(currentCase, transcriptText);

  try {
    const raw = await callClaude('당신은 정확하고 일관된 CPX 채점관입니다. 반드시 순수 JSON만 출력하세요.', [{role: 'user', content: gradingPrompt}]);
    let jsonText = raw.trim();
    const firstBrace = jsonText.indexOf('{');
    const lastBrace = jsonText.lastIndexOf('}');
    jsonText = jsonText.slice(firstBrace, lastBrace + 1);
    const result = JSON.parse(jsonText);
    renderGrading(result);
  } catch (e) {
    gradingBody.innerHTML = '<div class="hint">채점 중 오류: ' + e.message + '</div>';
  } finally {
    startBtn.disabled = false;
    caseSelect.disabled = false;
  }
});

function renderGrading(r) {
  gradingBody.innerHTML = `
    <div class="score-total">${r.total} / 100</div>
    <div class="domain-bar">
      <div class="domain-pill">병력청취 <b>${r.history_taking.score}</b>/40</div>
      <div class="domain-pill">신체진찰 <b>${r.physical_exam.score}</b>/20</div>
      <div class="domain-pill">PPI <b>${r.ppi.score}</b>/20</div>
      <div class="domain-pill">임상추론 <b>${r.clinical_reasoning.score}</b>/20</div>
    </div>
    <table>
      <tr><th style="width:120px;">영역</th><th>평가 근거</th></tr>
      <tr><td>병력청취</td><td>${r.history_taking.detail}</td></tr>
      <tr><td>신체진찰</td><td>${r.physical_exam.detail}</td></tr>
      <tr><td>PPI</td><td>${r.ppi.detail}</td></tr>
      <tr><td>임상추론</td><td>${r.clinical_reasoning.detail}</td></tr>
    </table>
    <p class="small"><b>피드백:</b> ${r.feedback}</p>
  `;
}
</script>
</body>
</html>
"""

html = html.replace("__CASES_JSON__", CASES_JSON).replace("__KEY_JSON__", KEY_JSON)

with open("../index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("written", len(html), "chars")
