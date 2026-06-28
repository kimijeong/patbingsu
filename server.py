"""
CPX 시뮬레이션 FastAPI 서버
실행: python -m uvicorn server:app --host 0.0.0.0 --port 8001
환경변수: ANTHROPIC_API_KEY
"""
import os, json, random, sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE / "scoring"))

from scorer import score as run_score, to_json as score_to_json
from patient_prompt import generate_patient_system_prompt

# ── APP ──────────────────────────────────────────────────
app = FastAPI(title="CPX Simulation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/ui", StaticFiles(directory=str(BASE / "ui")), name="ui")

@app.get("/")
def serve_index():
    return FileResponse(str(BASE / "index.html"))

# ── 시나리오 로드 ─────────────────────────────────────────
SCENARIOS_DIR = BASE / "scenarios_book"

def load_scenarios() -> list:
    out = []
    for f in sorted(SCENARIOS_DIR.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"[skip] {f.name}: {e}")
    print(f"[서버] 시나리오 {len(out)}개 로드")
    return out

SCENARIOS = load_scenarios()

def find_scenario(sid: str):
    s = next((x for x in SCENARIOS if x["scenario_id"] == sid), None)
    if not s:
        raise HTTPException(404, f"scenario '{sid}' not found")
    return s

# ── Anthropic 클라이언트 ──────────────────────────────────
def get_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)

# ── ENDPOINTS ────────────────────────────────────────────

@app.get("/api/scenarios")
def list_scenarios(category: Optional[str] = None):
    pool = SCENARIOS
    if category:
        pool = [s for s in pool if s.get("category") == category]
    return [
        {
            "id":       s["scenario_id"],
            "category": s.get("category", ""),
            "name":     s["patient"]["name"],
            "age":      s["patient"]["age"],
            "gender":   s["patient"]["gender"],
        }
        for s in pool
    ]


@app.get("/api/scenario/random")
def random_scenario(category: Optional[str] = None):
    pool = SCENARIOS
    if category:
        pool = [s for s in pool if s.get("category") == category]
    if not pool:
        raise HTTPException(404, "no scenarios found")
    s = random.choice(pool)
    return _public_scenario(s)


@app.get("/api/scenario/{scenario_id}")
def get_scenario(scenario_id: str):
    return _public_scenario(find_scenario(scenario_id))


def _public_scenario(s: dict) -> dict:
    p = s["patient"]
    return {
        "scenario_id":    s["scenario_id"],
        "category":       s.get("category", ""),
        "chief_complaint": s.get("chief_complaint", ""),
        "patient": {
            "name":       p["name"],
            "age":        p["age"],
            "gender":     p["gender"],
            "vitals":     p.get("vitals", {}),
            "appearance": p.get("appearance", ""),
        },
        "nonverbal_expressions": s.get("nonverbal_expressions", {}),
    }


# ── CHAT ─────────────────────────────────────────────────

class ChatMsg(BaseModel):
    role: str     # "user" | "assistant"
    content: str

class ChatReq(BaseModel):
    scenario_id: str
    history: List[ChatMsg] = []
    message: str

@app.post("/api/chat")
async def chat(req: ChatReq):
    scenario = find_scenario(req.scenario_id)
    system = generate_patient_system_prompt(scenario)

    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    try:
        client = get_anthropic_client()
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        return {"reply": resp.content[0].text}
    except Exception as e:
        print(f"[Anthropic ERROR] {type(e).__name__}: {e}")
        raise HTTPException(500, f"{type(e).__name__}: {e}")


# ── SCORE ─────────────────────────────────────────────────

class ScoreReq(BaseModel):
    scenario_id: str
    transcript: List[str]

@app.post("/api/score")
def score_session(req: ScoreReq):
    scenario = find_scenario(req.scenario_id)
    report = run_score(req.transcript, scenario)
    raw = score_to_json(report)

    secs = raw.get("sections", {})
    hx  = secs.get("history", {})
    ex  = secs.get("physical_exam", {})
    inf = secs.get("information", {})
    ppi = secs.get("ppi", {})

    return {
        "scenario_id":      req.scenario_id,
        "hidden_diagnosis": scenario.get("hidden_diagnosis", ""),
        "total_score":      raw.get("total_score", 0),
        "total_max":        raw.get("total_max", 0),
        "percentage":       raw.get("percentage", 0),
        "scores": {
            "history":          hx.get("score", 0),
            "history_max":      hx.get("max", 0),
            "exam":             ex.get("score", 0),
            "exam_max":         ex.get("max", 0),
            "information":      inf.get("score", 0),
            "information_max":  inf.get("max", 0),
            "ppi":              ppi.get("score", 0),
            "ppi_max":          ppi.get("max", 0),
        },
        "detail": secs,
    }


# ── RUN ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
