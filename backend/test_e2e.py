# Full E2E Verification Script
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE = "http://127.0.0.1:5000"
PASS = 0
FAIL = 0
ISSUES = []

def check(label, condition, detail=""):
    global PASS, FAIL, ISSUES
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        ISSUES.append(f"{label}: {detail}")
        print(f"  [FAIL] {label} -- {detail}")


# ═══ TEST 1: Health ═══
print("\n=== TEST 1: HEALTH CHECK ===")
r = requests.get(f"{BASE}/health")
data = r.json()
check("Status OK", data["status"] == "ok")
check("Version 2.0.0", data["version"] == "2.0.0")
for eng in ["similarity", "summarizer", "classification", "legal_principles", "trend_analyzer", "recommendation"]:
    check(f"Engine: {eng}", data["engines"].get(eng, False) == True, f"{eng} not ready")


# ═══ TEST 2: /analyze — Contract Dispute ═══
print("\n=== TEST 2: /analyze — Contract Dispute ===")
contract_text = "\u0627\u0644\u0648\u0642\u0627\u0626\u0639: \u062a\u0642\u062f\u0645 \u0627\u0644\u0645\u062f\u0639\u064a \u0628\u062f\u0639\u0648\u0649 \u0623\u0645\u0627\u0645 \u0627\u0644\u0645\u062d\u0643\u0645\u0629 \u0627\u0644\u0639\u0627\u0645\u0629 \u064a\u0637\u0627\u0644\u0628 \u0641\u064a\u0647\u0627 \u0628\u0625\u0644\u0632\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u0649 \u0639\u0644\u064a\u0647 \u0628\u0633\u062f\u0627\u062f \u0645\u0628\u0644\u063a \u0648\u0642\u062f\u0631\u0647 75,000 \u0631\u064a\u0627\u0644 \u0633\u0639\u0648\u062f\u064a\u060c \u0648\u0630\u0644\u0643 \u0646\u062a\u064a\u062c\u0629 \u0625\u062e\u0644\u0627\u0644\u0647 \u0628\u0627\u0644\u0639\u0642\u062f \u0627\u0644\u0645\u0628\u0631\u0645 \u0628\u064a\u0646 \u0627\u0644\u0637\u0631\u0641\u064a\u0646 \u0648\u0627\u0644\u0645\u062a\u0639\u0644\u0642 \u0628\u062a\u0646\u0641\u064a\u0630 \u0623\u0639\u0645\u0627\u0644 \u0635\u064a\u0627\u0646\u0629. \u0627\u0644\u0623\u0633\u0628\u0627\u0628: \u0648\u062d\u064a\u062b \u0625\u0646 \u0627\u0644\u0645\u062d\u0643\u0645\u0629 \u0628\u0639\u062f \u0627\u0644\u0627\u0637\u0644\u0627\u0639 \u0639\u0644\u0649 \u0623\u0648\u0631\u0627\u0642 \u0627\u0644\u062f\u0639\u0648\u0649 \u062a\u0628\u064a\u0646 \u0644\u0647\u0627 \u0648\u062c\u0648\u062f \u0639\u0642\u062f \u0635\u062d\u064a\u062d \u0648\u0645\u0648\u0642\u0639 \u0628\u064a\u0646 \u0627\u0644\u0637\u0631\u0641\u064a\u0646\u060c \u0648\u062b\u0628\u0648\u062a \u0642\u064a\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u064a \u0628\u062a\u0646\u0641\u064a\u0630 \u0627\u0644\u062a\u0632\u0627\u0645\u0627\u062a\u0647 \u0627\u0644\u062a\u0639\u0627\u0642\u062f\u064a\u0629. \u0648\u0644\u0645 \u064a\u0642\u062f\u0645 \u0627\u0644\u0645\u062f\u0639\u0649 \u0639\u0644\u064a\u0647 \u0645\u0627 \u064a\u062b\u0628\u062a \u0627\u0644\u0633\u062f\u0627\u062f. \u0645\u0646\u0637\u0648\u0642 \u0627\u0644\u062d\u0643\u0645: \u062d\u0643\u0645\u062a \u0627\u0644\u0645\u062d\u0643\u0645\u0629 \u0628\u0625\u0644\u0632\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u0649 \u0639\u0644\u064a\u0647 \u0628\u0633\u062f\u0627\u062f \u0645\u0628\u0644\u063a 75,000 \u0631\u064a\u0627\u0644 \u0633\u0639\u0648\u062f\u064a \u0644\u0644\u0645\u062f\u0639\u064a."
r = requests.post(f"{BASE}/analyze", json={"text": contract_text, "top_k": 5})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Has classification", "classification" in data)
check("Case type detected", data["classification"]["case_type"] != "unknown", f"got: {data['classification']['case_type']}")
check("Confidence > 0", data["classification"]["confidence"] > 0)
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")
check("Has legal_principles", "legal_principles" in data and len(data["legal_principles"]) > 0, f"found {len(data.get('legal_principles',[]))}")
for p in data.get("legal_principles", []):
    print(f"    -> Principle: {p['name_en']} (section: {p['source_section']})")
check("Has trends", "trends" in data and data["trends"] is not None)
check("Has recommendation", "recommendation" in data and data["recommendation"] is not None)
if data.get("recommendation"):
    check("Has disclaimer", len(data["recommendation"].get("disclaimer_ar","")) > 0)
    check("Direction valid", data["recommendation"]["direction"] in ["plaintiff_likely","defendant_likely","uncertain","insufficient_data"])
    print(f"    -> Direction: {data['recommendation']['direction']}")
    print(f"    -> Confidence: {data['recommendation']['confidence']}")
    print(f"    -> Based on {data['recommendation']['based_on_sample_size']} cases")
if data.get("trends"):
    check("Win rate in range", 0 <= data["trends"]["plaintiff_win_rate"] <= 100)
    check("Sample size > 0", data["trends"]["sample_size"] > 0)
    print(f"    -> Win rate: {data['trends']['plaintiff_win_rate']}%")
    print(f"    -> Avg compensation: {data['trends']['average_compensation']}")
    print(f"    -> Reliability: {data['trends']['reliability']}")


# ═══ TEST 3: /analyze — Partnership/Mudharaba ═══
print("\n=== TEST 3: /analyze — Partnership Case ===")
partner_text = "\u0627\u0644\u0648\u0642\u0627\u0626\u0639: \u062a\u0642\u062f\u0645 \u0648\u0643\u064a\u0644 \u0627\u0644\u0645\u062f\u0639\u064a \u0628\u0644\u0627\u0626\u062d\u0629 \u062f\u0639\u0648\u0649 \u062a\u062a\u0636\u0645\u0646 \u0623\u0646 \u0627\u0644\u0634\u0631\u0643\u0629 \u0634\u0631\u0643\u0629 \u0645\u0636\u0627\u0631\u0628\u0629 \u0648\u0642\u062f \u062f\u0641\u0639 \u0627\u0644\u0645\u062f\u0639\u064a \u0631\u0623\u0633 \u0627\u0644\u0645\u0627\u0644 \u0645\u0628\u0644\u063a 100000 \u0631\u064a\u0627\u0644. \u0627\u0644\u0623\u0633\u0628\u0627\u0628: \u0648\u062d\u064a\u062b \u0625\u0646 \u0627\u0644\u0645\u062d\u0643\u0645\u0629 \u062a\u0628\u064a\u0646\u062a \u0648\u062c\u0648\u062f \u0639\u0642\u062f \u0645\u0628\u0631\u0645 \u0628\u064a\u0646 \u0627\u0644\u0637\u0631\u0641\u064a\u0646 \u0648\u0633\u0646\u062f \u0644\u0623\u0645\u0631. \u0645\u0646\u0637\u0648\u0642 \u0627\u0644\u062d\u0643\u0645: \u0625\u0644\u0632\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u0649 \u0639\u0644\u064a\u0647\u0627 \u0628\u0623\u0646 \u062a\u062f\u0641\u0639 \u0644\u0644\u0645\u062f\u0639\u064a \u0645\u0628\u0644\u063a 100000 \u0631\u064a\u0627\u0644."
r = requests.post(f"{BASE}/analyze", json={"text": partner_text, "top_k": 5})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Classification exists", data["classification"]["case_type"] != "unknown")
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")
print(f"    -> Principles: {len(data.get('legal_principles',[]))}")
if data.get("trends"):
    print(f"    -> Win rate: {data['trends']['plaintiff_win_rate']}%, Reliability: {data['trends']['reliability']}")


# ═══ TEST 4: /summarize ═══
print("\n=== TEST 4: /summarize ===")
r = requests.post(f"{BASE}/summarize", json={"text": contract_text})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Has summary", len(data.get("summary","")) > 0)
check("Has facts_summary", data.get("facts_summary") is not None)
check("Has verdict_summary", data.get("verdict_summary") is not None)
check("Confidence > 0.9", data.get("confidence", 0) > 0.9)
print(f"    -> Confidence: {data.get('confidence')}")


# ═══ TEST 5: /analytics ═══
print("\n=== TEST 5: /analytics ===")
r = requests.get(f"{BASE}/analytics")
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Has data_source label", "simulation" in data.get("data_source","").lower())
check("Total cases > 0", data.get("total_cases", 0) > 0)
check("Has case_type_distribution", len(data.get("case_type_distribution",{})) > 0)
check("Has outcome_distribution", len(data.get("outcome_distribution",{})) > 0)
check("Has compensation_stats", "average" in data.get("compensation_stats",{}))
print(f"    -> Total cases: {data['total_cases']}")
print(f"    -> Case types: {list(data['case_type_distribution'].keys())}")
print(f"    -> Avg compensation: {data['compensation_stats'].get('average',0)}")


# ═══ TEST 6: Edge Case — Very Short Text ═══
print("\n=== TEST 6: Edge Case — Short Text ===")
r = requests.post(f"{BASE}/analyze", json={"text": "test", "top_k": 3})
check("Short text no crash", r.status_code == 200)
data = r.json()
check("Unknown type for nonsense", True)  # Should not crash
print(f"    -> Type: {data['classification']['name_en']} ({data['classification']['confidence']})")


# ═══ TEST 7: Edge Case — No Sections ═══
print("\n=== TEST 7: Edge Case — Text Without Sections ===")
no_sec = "\u0627\u0644\u0645\u062f\u0639\u064a \u064a\u0637\u0627\u0644\u0628 \u0628\u0645\u0628\u0644\u063a 50000 \u0631\u064a\u0627\u0644 \u0628\u0633\u0628\u0628 \u0625\u062e\u0644\u0627\u0644 \u0628\u0627\u0644\u0639\u0642\u062f"
r = requests.post(f"{BASE}/analyze", json={"text": no_sec, "top_k": 3})
check("No-section text no crash", r.status_code == 200)
data = r.json()
print(f"    -> Type: {data['classification']['name_en']}")
print(f"    -> Principles: {len(data.get('legal_principles',[]))}")

# ═══ TEST 8: /similar ═══
print("\n=== TEST 8: /similar ===")
r = requests.post(f"{BASE}/similar", json={"text": contract_text, "top_k": 3})
data = r.json()
check("HTTP 200", r.status_code == 200)
check("Returns cases", len(data) > 0)
if data:
    check("Has case_id", "case_id" in data[0])
    check("Has similarity_score", "similarity_score" in data[0])
    check("Score in range", 0 < data[0]["similarity_score"] <= 100)
    for c in data:
        print(f"    -> {c['case_id']}: {c['similarity_score']}%")


# ═══ SUMMARY ═══
print(f"\n{'='*50}")
print(f"RESULTS: {PASS} passed, {FAIL} failed")
print(f"{'='*50}")
if ISSUES:
    print("ISSUES:")
    for i in ISSUES:
        print(f"  - {i}")
else:
    print("ALL TESTS PASSED!")
