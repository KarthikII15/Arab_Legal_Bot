# Full E2E Verification Script — Enhanced with Labor Case + Performance Profiling
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE = "http://127.0.0.1:5001"
PASS = 0
FAIL = 0
ISSUES = []
TIMINGS = {}

def check(label, condition, detail=""):
    global PASS, FAIL, ISSUES
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        ISSUES.append(f"{label}: {detail}")
        print(f"  [FAIL] {label} -- {detail}")

def timed_request(method, url, **kwargs):
    """Make request and return (response, elapsed_seconds)."""
    t0 = time.time()
    if method == "GET":
        r = requests.get(url, **kwargs)
    else:
        r = requests.post(url, **kwargs)
    elapsed = time.time() - t0
    return r, elapsed


# ═══ TEST 1: Health ═══
print("\n=== TEST 1: HEALTH CHECK ===")
r, t = timed_request("GET", f"{BASE}/health")
data = r.json()
check("Status OK", data["status"] == "ok")
check("Version 2.0.0", data["version"] == "2.0.0")
for eng in ["similarity", "summarizer", "classification", "legal_principles", "trend_analyzer", "recommendation"]:
    check(f"Engine: {eng}", data["engines"].get(eng, False) == True, f"{eng} not ready")
TIMINGS["health"] = t
print(f"    -> Time: {t:.3f}s")


# ═══ TEST 2: /analyze — Contract Dispute ═══
print("\n=== TEST 2: /analyze — Contract Dispute ===")
contract_text = """الوقائع: تقدم المدعي بدعوى أمام المحكمة العامة يطالب فيها بإلزام المدعى عليه بسداد مبلغ وقدره 75,000 ريال سعودي، وذلك نتيجة إخلاله بالعقد المبرم بين الطرفين والمتعلق بتنفيذ أعمال صيانة. الأسباب: وحيث إن المحكمة بعد الاطلاع على أوراق الدعوى تبين لها وجود عقد صحيح وموقع بين الطرفين، وثبوت قيام المدعي بتنفيذ التزاماته التعاقدية. ولم يقدم المدعى عليه ما يثبت السداد. منطوق الحكم: حكمت المحكمة بإلزام المدعى عليه بسداد مبلغ 75,000 ريال سعودي للمدعي."""
r, t = timed_request("POST", f"{BASE}/analyze", json={"text": contract_text, "top_k": 5})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Has classification", "classification" in data)
check("Case type detected", data["classification"]["case_type"] != "unknown", f"got: {data['classification']['case_type']}")
check("Confidence > 0", data["classification"]["confidence"] > 0)
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")
lp_count = len(data.get("legal_principles", []))
check("Has legal_principles", lp_count > 0, f"found {lp_count}")
for p in data.get("legal_principles", []):
    print(f"    -> Principle: {p['name_en']} (section: {p['source_section']})")
check("Has trends", "trends" in data and data["trends"] is not None)
check("Has recommendation", "recommendation" in data and data["recommendation"] is not None)
if data.get("recommendation"):
    check("Has disclaimer", len(data["recommendation"].get("disclaimer_ar", "")) > 0)
    check("Direction valid", data["recommendation"]["direction"] in ["plaintiff_likely", "defendant_likely", "uncertain", "insufficient_data"])
    print(f"    -> Direction: {data['recommendation']['direction']}")
    print(f"    -> Confidence: {data['recommendation']['confidence']}")
    print(f"    -> Based on {data['recommendation']['based_on_sample_size']} cases")
if data.get("trends"):
    check("Win rate in range", 0 <= data["trends"]["plaintiff_win_rate"] <= 100)
    check("Sample size > 0", data["trends"]["sample_size"] > 0)
    print(f"    -> Win rate: {data['trends']['plaintiff_win_rate']}%")
    print(f"    -> Avg compensation: {data['trends']['average_compensation']}")
    print(f"    -> Reliability: {data['trends']['reliability']}")
TIMINGS["analyze_contract"] = t
print(f"    -> Response time: {t:.3f}s")


# ═══ TEST 3: /analyze — Labor Case (NEW) ═══
print("\n=== TEST 3: /analyze — Labor Case ===")
labor_text = """الوقائع: تقدم المدعي بدعوى ضد صاحب العمل يطالب فيها بمكافأة نهاية الخدمة وبدل الإجازة والتعويض عن فصل تعسفي بعد خدمة 5 سنوات. وذكر أنه تم إنهاء خدماته دون سبب مشروع وبالمخالفة لنظام العمل. الأسباب: بعد الاطلاع على عقد العمل ونظام العمل تبين أن الفصل كان تعسفياً ومخالفاً للمادة 77 من نظام العمل. منطوق الحكم: حكمت المحكمة بإلزام المدعى عليه بدفع مكافأة نهاية الخدمة وبدل الإجازة وتعويض قدره 50000 ريال."""
r, t = timed_request("POST", f"{BASE}/analyze", json={"text": labor_text, "top_k": 5})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Classification exists", data["classification"]["case_type"] != "unknown")
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")
print(f"    -> Principles: {len(data.get('legal_principles', []))}")
if data.get("trends"):
    print(f"    -> Win rate: {data['trends']['plaintiff_win_rate']}%, Reliability: {data['trends']['reliability']}")
if data.get("recommendation"):
    print(f"    -> Direction: {data['recommendation']['direction']}")
    print(f"    -> Confidence: {data['recommendation']['confidence']}")
TIMINGS["analyze_labor"] = t
print(f"    -> Response time: {t:.3f}s")


# ═══ TEST 4: /analyze — Traffic Accident ═══
print("\n=== TEST 4: /analyze — Traffic Accident ===")
traffic_text = """الوقائع: تقدم المدعي يطالب بالتعويض عن الأضرار الناتجة عن حادث مروري تسبب فيه المدعى عليه بسبب قيادته المتهورة المركبة، حيث أسفر الحادث عن إصابات جسدية وأضرار مادية في سيارة المدعي بمبلغ 30000 ريال. الأسباب: ثبت من تقرير المرور أن المدعى عليه هو المتسبب في الحادث. منطوق الحكم: حكمت المحكمة بإلزام المدعى عليه بدفع تعويض قدره 30000 ريال للمدعي عن الأضرار."""
r, t = timed_request("POST", f"{BASE}/analyze", json={"text": traffic_text, "top_k": 5})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Classification exists", data["classification"]["case_type"] != "unknown")
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")
print(f"    -> Principles: {len(data.get('legal_principles', []))}")
TIMINGS["analyze_traffic"] = t
print(f"    -> Response time: {t:.3f}s")


# ═══ TEST 5: /summarize ═══
print("\n=== TEST 5: /summarize ===")
r, t = timed_request("POST", f"{BASE}/summarize", json={"text": contract_text})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Has summary", len(data.get("summary", "")) > 0)
check("Has facts_summary", data.get("facts_summary") is not None)
check("Has verdict_summary", data.get("verdict_summary") is not None)
check("Confidence > 0.9", data.get("confidence", 0) > 0.9)
print(f"    -> Confidence: {data.get('confidence')}")
TIMINGS["summarize"] = t
print(f"    -> Response time: {t:.3f}s")


# ═══ TEST 6: /analytics ═══
print("\n=== TEST 6: /analytics ===")
r, t = timed_request("GET", f"{BASE}/analytics")
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Has data_source label", "simulation" in data.get("data_source", "").lower())
check("Total cases > 0", data.get("total_cases", 0) > 0)
check("Has case_type_distribution", len(data.get("case_type_distribution", {})) > 0)
check("Has outcome_distribution", len(data.get("outcome_distribution", {})) > 0)
check("Has compensation_stats", "average" in data.get("compensation_stats", {}))
print(f"    -> Total cases: {data['total_cases']}")
print(f"    -> Case types: {list(data['case_type_distribution'].keys())}")
print(f"    -> Outcome dist: {data['outcome_distribution']}")
print(f"    -> Avg compensation: {data['compensation_stats'].get('average', 0)}")
TIMINGS["analytics"] = t
print(f"    -> Response time: {t:.3f}s")


# ═══ TEST 7: Edge Case — Very Short Text ═══
print("\n=== TEST 7: Edge Case — Short Text ===")
r, t = timed_request("POST", f"{BASE}/analyze", json={"text": "test", "top_k": 3})
check("Short text no crash", r.status_code == 200)
data = r.json()
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")
TIMINGS["edge_short"] = t


# ═══ TEST 8: Edge Case — No Sections ═══
print("\n=== TEST 8: Edge Case — Text Without Sections ===")
no_sec = "المدعي يطالب بمبلغ 50000 ريال بسبب إخلال بالعقد"
r, t = timed_request("POST", f"{BASE}/analyze", json={"text": no_sec, "top_k": 3})
check("No-section text no crash", r.status_code == 200)
data = r.json()
print(f"    -> Type: {data['classification']['name_en']}")
print(f"    -> Principles: {len(data.get('legal_principles', []))}")
TIMINGS["edge_nosection"] = t


# ═══ TEST 9: Edge Case — Unknown/Empty-ish Text ═══
print("\n=== TEST 9: Edge Case — No Monetary Amount ===")
no_money = """الوقائع: تقدم المدعي بطلب إثبات ملكية عقار. الأسباب: بعد الاطلاع على الصكوك. منطوق الحكم: رفض الدعوى لعدم كفاية الأدلة."""
r, t = timed_request("POST", f"{BASE}/analyze", json={"text": no_money, "top_k": 3})
check("No money text no crash", r.status_code == 200)
data = r.json()
print(f"    -> Type: {data['classification']['name_en']}")
if data.get("trends"):
    print(f"    -> Avg compensation: {data['trends']['average_compensation']}")
TIMINGS["edge_nomoney"] = t


# ═══ TEST 10: /similar ═══
print("\n=== TEST 10: /similar ===")
r, t = timed_request("POST", f"{BASE}/similar", json={"text": contract_text, "top_k": 3})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Returns cases", len(data) > 0)
if data:
    check("Has case_id", "case_id" in data[0])
    check("Has similarity_score", "similarity_score" in data[0])
    check("Score in range", 0 < data[0]["similarity_score"] <= 100)
    for c in data:
        print(f"    -> {c['case_id']}: {c['similarity_score']}%")
TIMINGS["similar"] = t
print(f"    -> Response time: {t:.3f}s")


# ═══ PERFORMANCE PROFILE ═══
print(f"\n{'='*50}")
print("PERFORMANCE PROFILE")
print(f"{'='*50}")
for k, v in TIMINGS.items():
    bar = "█" * int(v * 5)
    print(f"  {k:25s} {v:6.3f}s  {bar}")

total_time = sum(TIMINGS.values())
print(f"\n  {'TOTAL':25s} {total_time:6.3f}s")


# ═══ SUMMARY ═══
print(f"\n{'='*50}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
print(f"{'='*50}")
if ISSUES:
    print("ISSUES:")
    for i in ISSUES:
        print(f"  - {i}")
else:
    print("ALL TESTS PASSED! ✅")
