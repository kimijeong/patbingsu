# -*- coding: utf-8 -*-
import json, re, os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CheckResult:
    item: str
    passed: bool
    grade: str
    score_earned: float
    score_max: float
    matched_keywords: List[str] = field(default_factory=list)

@dataclass
class ScoreReport:
    scenario_id: str
    patient_name: str
    category: str
    is_female: bool = False
    history: list = field(default_factory=list)
    physical_exam: list = field(default_factory=list)
    information: list = field(default_factory=list)
    ppi: list = field(default_factory=list)

    def _sum(self, lst, attr):
        return sum(getattr(r, attr) for r in lst)

    @property
    def history_score(self): return self._sum(self.history, "score_earned")
    @property
    def history_max(self): return self._sum(self.history, "score_max")
    @property
    def exam_score(self): return self._sum(self.physical_exam, "score_earned")
    @property
    def exam_max(self): return self._sum(self.physical_exam, "score_max")
    @property
    def info_score(self): return self._sum(self.information, "score_earned")
    @property
    def info_max(self): return self._sum(self.information, "score_max")
    @property
    def ppi_score(self): return self._sum(self.ppi, "score_earned")
    @property
    def ppi_max(self): return self._sum(self.ppi, "score_max")
    @property
    def total_score(self): return self.history_score + self.exam_score + self.info_score + self.ppi_score
    @property
    def total_max(self): return self.history_max + self.exam_max + self.info_max + self.ppi_max


# ---- Standard checklists (based on CPX rubric) ----

STANDARD_HISTORY = [
    {"item": "Onset (만성/급성/반복성) + 발병시 활동",
     "kw_A": ["갑자기","서서히","만성","급성","반복","언제부터"],
     "kw_B": ["활동","운동","식사 중","자다가","일하다","먹다가","뭐 하다가"],
     "full": 1.0, "partial": 0.5},
    {"item": "Duration - 지속시간",
     "kw_A": ["얼마나","지속","계속","몇 분","몇 시간","언제까지","오래"],
     "kw_B": [], "full": 1.0, "partial": None},
    {"item": "Location + Radiation",
     "kw_A": ["어디","위치","짚어","어느 쪽","어디가"],
     "kw_B": ["퍼지","방사","뻗치","등","어깨","다른 데"],
     "full": 1.0, "partial": 0.5},
    {"item": "Character - 통증양상 및 변화양상",
     "kw_A": ["어떻게 아프","양상","콕콕","쥐어짜","타는","쓰리","찌르는","묵직","베이","느낌"],
     "kw_B": [], "full": 1.0, "partial": None},
    {"item": "NRS - 심한정도 0~10점",
     "kw_A": ["nrs","몇 점","10점","점수","얼마나 심","숫자로"],
     "kw_B": [], "full": 1.0, "partial": None},
    {"item": "악화요인 + 완화요인",
     "kw_A": ["악화","심해지","더 아프","먹으면","움직이면","누르면","먹고 나서"],
     "kw_B": ["완화","나아지","덜 아프","쉬면","편해지","좋아지"],
     "full": 1.0, "partial": 0.5},
    {"item": "이전에 비슷한 통증 경험 여부",
     "kw_A": ["이전","전에도","예전","과거","비슷한","경험","처음"],
     "kw_B": [], "full": 1.0, "partial": None},
]

FEMALE_HX = {
    "item": "[여성] 월경력(LMP) + 임신가능성 (우선 확인!)",
    "kw_A": ["생리","월경","lmp","마지막 생리"],
    "kw_B": ["임신","피임","임신 가능"],
    "full": 1.0, "partial": 0.5
}

ASSOC_CATEGORIES = {
    "구역/구토":  ["구역","구토","메스꺼","토"],
    "체중변화":   ["체중","살","빠졌","쪘","몸무게"],
    "발열":       ["열","발열","오한","체온"],
    "기타":       ["황달","혈변","흑색변","혈뇨","방귀","배변","식욕","변비","설사",
                   "어지러","두근","숨","질출혈","생리","설사"],
}

STANDARD_EXAM = [
    {"item": "복부 청진 (4군데, 아픈곳 마지막)",
     "kw": ["청진","장음","소리 들"],
     "kw_quad": ["우상","좌상","우하","좌하","사분","전체","돌아가"],
     "full": 3.0, "partial": 1.5},
    {"item": "복부 타진 (4군데, 아픈곳 마지막)",
     "kw": ["타진","두드려","탁음","고장음"],
     "kw_quad": ["우상","좌상","우하","좌하","전체","돌아가"],
     "full": 2.0, "partial": 1.0},
    {"item": "복부 촉진 (4군데, 아픈곳 마지막)",
     "kw": ["촉진","눌러","만져","누르"],
     "kw_quad": ["우상","좌상","우하","좌하","전체","돌아가","순서"],
     "full": 3.0, "partial": 1.5},
    {"item": "복부 압통 / 반발통",
     "kw_td":  ["압통","눌러","촉진"],
     "kw_rtd": ["반동","rebound","손 뗄","반발"],
     "full": 3.0, "partial": 1.5, "dual": True},
    {"item": "Murphy's sign",
     "kw": ["murphy","머피","숨 들이쉬","흡기","우상복부 누르면서 숨"],
     "kw_quad": [],
     "full": 2.0, "partial": 1.0},
    {"item": "CVAT (늑골척추각 압통)",
     "kw": ["cvat","등 두드려","늑골척추각","등 뒤"],
     "kw_quad": [],
     "full": 2.0, "partial": 1.0},
]

PPI_ITEMS = [
    {"item": "효율적 문진 및 경청", "kw": ["맞나요","말씀해 주세요","확인","제가 이해했나요"]},
    {"item": "환자 생각/걱정 파악", "kw": ["걱정되시","어떻게 생각","기분","무엇이 걱정","혹시 궁금"]},
    {"item": "이해하기 쉽게 설명", "kw": ["쉽게 말씀드리면","이해가 되셨나요","궁금한 것"]},
    {"item": "유대관계 형성",       "kw": ["힘드셨겠어요","걱정되시겠어요","이해합니다","공감"]},
    {"item": "면담 체계적 진행",    "kw": ["정리해 보면","요약","다음으로","이제"]},
    {"item": "신체진찰 태도",       "kw": ["손 씻","설명해 드릴게요","불편하시면","편하게"]},
]


# ---- Utils ----

def norm(t): return re.sub(r"\s+", " ", t.lower().strip())

def search(transcript, keywords):
    found = []
    for utt in transcript:
        n = norm(utt)
        for kw in keywords:
            if norm(kw) in n and kw not in found:
                found.append(kw)
    return found

def shorten(keywords):
    prefixes = ["급성 ","만성 ","일차성 ","기능성 ","알코올성 "]
    suffixes = [" 천공"," 파열"," 농양"," 염증"]
    result = list(keywords)
    for kw in keywords:
        s = kw
        for p in prefixes: s = s.replace(p, "")
        for x in suffixes: s = s.replace(x, "")
        s = s.strip()
        if s and s != kw: result.append(s)
    return result


# ---- Scoring functions ----

def score_history(transcript, scenario):
    results = []
    is_female = scenario.get("patient", {}).get("gender") in ["여","F","female"]

    if is_female:
        itm = FEMALE_HX
        fA = search(transcript, itm["kw_A"])
        fB = search(transcript, itm["kw_B"])
        if fA and fB:   g, e = "우수", itm["full"]
        elif fA or fB:  g, e = "보통", itm["partial"]
        else:           g, e = "미시행", 0.0
        results.append(CheckResult(itm["item"], g=="우수", g, e, itm["full"], fA+fB))

    for itm in STANDARD_HISTORY:
        fA = search(transcript, itm["kw_A"])
        fB = search(transcript, itm.get("kw_B", []))
        sp = itm.get("partial")
        has_B_def = bool(itm.get("kw_B"))

        if fA and (not has_B_def or fB):
            g, e = "우수", itm["full"]
        elif fA and has_B_def and not fB and sp:
            g, e = "보통", sp
        elif fB and not fA and sp:
            g, e = "보통", sp
        elif fA:
            g, e = "우수", itm["full"]
        else:
            g, e = "미시행", 0.0
        results.append(CheckResult(itm["item"], g=="우수", g, e, itm["full"], fA+fB))

    hits = {}
    for cat, kws in ASSOC_CATEGORIES.items():
        f = search(transcript, kws)
        if f: hits[cat] = f
    n = len(hits)
    if n >= 3:   g, e = "우수", 1.0
    elif n >= 1: g, e = "보통", 0.5
    else:        g, e = "미시행", 0.0
    all_kws = [kw for kws in hits.values() for kw in kws]
    results.append(CheckResult(f"동반증상 ({n}가지 확인, 3가지이상=우수)", g=="우수", g, e, 1.0, all_kws))

    for b in scenario.get("scoring", {}).get("history_checklist", []):
        f = search(transcript, b.get("keywords", []))
        label = b.get("category") or b.get("item", "")
        sc = b.get("score", 0)
        results.append(CheckResult(f"[진단특이] {label}", bool(f), "우수" if f else "미시행",
                                   sc if f else 0, sc, f))
    return results


def score_exam(transcript, scenario):
    results = []
    for itm in STANDARD_EXAM:
        if itm.get("dual"):
            fTd  = search(transcript, itm["kw_td"])
            fRtd = search(transcript, itm["kw_rtd"])
            if fTd and fRtd:   g, e = "우수", itm["full"]
            elif fTd or fRtd:  g, e = "보통", itm["partial"]
            else:              g, e = "미시행", 0.0
            results.append(CheckResult(itm["item"], g=="우수", g, e, itm["full"], fTd+fRtd))
        else:
            fM = search(transcript, itm["kw"])
            fQ = search(transcript, itm.get("kw_quad", []))
            if itm.get("kw_quad"):
                if fM and fQ:   g, e = "우수", itm["full"]
                elif fM:        g, e = "보통", itm["partial"]
                else:           g, e = "미시행", 0.0
            else:
                if fM:   g, e = "우수", itm["full"]
                else:    g, e = "미시행", 0.0
            results.append(CheckResult(itm["item"], g=="우수", g, e, itm["full"], fM+fQ))
    return results


def score_information(transcript, scenario):
    """
    정보제공 채점 (5점)
    1. 진단 선언 (1점): "OOO씨는 [병명]이 의심됩니다"
    2. 검사 + 근거 (2점): "[이유] 때문에 [검사]를 하겠습니다"
    3. 치료/다음 플랜 (2점): "수술을 고려하십시오" 등
    """
    results = []
    sc = scenario.get("scoring", {})
    top = sc.get("top_diagnoses") or scenario.get("top_diagnoses", [])
    patient_name = scenario.get("patient", {}).get("name", "")

    # 1. 진단 선언 (1점) - 병명 언급만 해도 ok, 낮은 배점
    diag_kws = shorten(top) + ["의심됩니다","생각됩니다","것 같습니다","으로 보입니다"]
    fD = search(transcript, diag_kws)
    # 우수: 환자 이름 + 진단명 함께 언급
    name_found = patient_name and search(transcript, [patient_name])
    if fD and name_found:
        g, e = "우수", 1.0
    elif fD:
        g, e = "보통", 0.5
    else:
        g, e = "미시행", 0.0
    results.append(CheckResult(
        f"진단 선언 (OOO씨는 [병명]이 의심됩니다)", g=="우수", g, e, 1.0, fD
    ))

    # 2. 검사 + 근거 (2점)
    # 우수: 검사명 + 이유/목적 함께 언급 ("~을 보기 위해", "~이 의심되어")
    reason_kws = ["위해","때문에","의심되어","확인하기 위해","보기 위해","알아보기 위해","평가하기 위해"]
    test_kws = sc.get("required_tests", [])
    fTest = search(transcript, test_kws)
    fReason = search(transcript, reason_kws)
    if fTest and fReason:
        g, e = "우수", 2.0
    elif fTest:
        g, e = "보통", 1.0
    else:
        g, e = "미시행", 0.0
    results.append(CheckResult(
        "검사 계획 + 근거 ([이유] 때문에 [검사]를 하겠습니다)", g=="우수", g, e, 2.0, fTest+fReason
    ))

    # 3. 치료/다음 플랜 (2점)
    # 우수: 치료명 + 권고 표현 ("고려하십시오", "필요합니다", "권유드립니다")
    plan_action_kws = ["고려","권유","입원","수술","약물","처방","의뢰","필요합니다","해야 합니다"]
    tx_kws = sc.get("required_treatments", [])
    fTx = search(transcript, tx_kws)
    fAction = search(transcript, plan_action_kws)
    if fTx and fAction:
        g, e = "우수", 2.0
    elif fTx or fAction:
        g, e = "보통", 1.0
    else:
        g, e = "미시행", 0.0
    results.append(CheckResult(
        "치료/다음 플랜 (수술을 고려하십시오 등)", g=="우수", g, e, 2.0, fTx+fAction
    ))

    return results


def score_ppi(transcript):
    results = []
    for itm in PPI_ITEMS:
        f = search(transcript, itm["kw"])
        results.append(CheckResult(itm["item"], bool(f), "우수" if f else "미시행",
                                   1.0 if f else 0.0, 1.0, f))
    return results


def score(transcript, scenario):
    report = ScoreReport(
        scenario_id=scenario.get("scenario_id",""),
        patient_name=scenario.get("patient",{}).get("name",""),
        category=scenario.get("category",""),
        is_female=scenario.get("patient",{}).get("gender") in ["여","F","female"],
    )
    report.history      = score_history(transcript, scenario)
    report.physical_exam = score_exam(transcript, scenario)
    report.information  = score_information(transcript, scenario)
    report.ppi          = score_ppi(transcript)
    return report


def format_report(report):
    lines = ["="*60,
             f"  CPX 채점  [{report.patient_name}] {report.category}",
             "="*60]
    def section(title, results, s, m):
        pct = round(s/m*100) if m else 0
        lines.append(f"\n[{title}]  {s:.1f}/{m:.0f}점  ({pct}%)")
        icons = {"우수":"●","보통":"△","미시행":"○"}
        for r in results:
            lines.append(f"  {icons.get(r.grade,'?')} {r.item}  ({r.score_earned:.1f}/{r.score_max:.1f})")
            if r.matched_keywords:
                lines.append(f"      -> {r.matched_keywords[:3]}")
    section("병력 청취",        report.history,      report.history_score, report.history_max)
    section("신체 진찰",        report.physical_exam, report.exam_score,   report.exam_max)
    section("정보 제공",        report.information,   report.info_score,   report.info_max)
    section("환자-의사 관계",   report.ppi,           report.ppi_score,    report.ppi_max)
    pct = round(report.total_score/report.total_max*100) if report.total_max else 0
    lines += ["","="*60,
              f"  총점: {report.total_score:.1f} / {report.total_max:.0f}점  ({pct}%)",
              "="*60]
    return "\n".join(lines)


def to_json(report):
    def ser(lst):
        return [{"item":r.item,"grade":r.grade,"score_earned":r.score_earned,
                 "score_max":r.score_max,"matched":r.matched_keywords} for r in lst]
    return {
        "scenario_id": report.scenario_id,
        "sections": {
            "history":      {"score":report.history_score, "max":report.history_max, "items":ser(report.history)},
            "physical_exam":{"score":report.exam_score,    "max":report.exam_max,    "items":ser(report.physical_exam)},
            "information":  {"score":report.info_score,    "max":report.info_max,    "items":ser(report.information)},
            "ppi":          {"score":report.ppi_score,     "max":report.ppi_max,     "items":ser(report.ppi)},
        },
        "total_score": report.total_score,
        "total_max":   report.total_max,
        "percentage":  round(report.total_score/report.total_max*100) if report.total_max else 0,
    }



if __name__ == "__main__":
    import sys
    base = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "../scenarios_book/acute_01.json")
    with open(path, encoding="utf-8") as f:
        scenario = f.read()
    import json as _json
    scenario = _json.loads(scenario)
    print("scenario loaded:", scenario.get("scenario_id"))
