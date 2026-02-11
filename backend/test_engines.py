# Quick test for all intelligence engines
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from classification_engine import classify_case
from legal_principles import extract_legal_principles
from trend_analyzer import detect_outcome, extract_compensation_amount

test = "\u062a\u0642\u062f\u0645 \u0627\u0644\u0645\u062f\u0639\u064a \u0628\u062f\u0639\u0648\u0649 \u064a\u0637\u0627\u0644\u0628 \u0641\u064a\u0647\u0627 \u0628\u0625\u0644\u0632\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u0649 \u0639\u0644\u064a\u0647 \u0628\u0633\u062f\u0627\u062f \u0645\u0628\u0644\u063a 75000 \u0631\u064a\u0627\u0644 \u0646\u062a\u064a\u062c\u0629 \u0625\u062e\u0644\u0627\u0644\u0647 \u0628\u0627\u0644\u0639\u0642\u062f \u0627\u0644\u0645\u0628\u0631\u0645 \u0628\u064a\u0646 \u0627\u0644\u0637\u0631\u0641\u064a\u0646. \u0648\u062d\u064a\u062b \u0625\u0646 \u0627\u0644\u0645\u062d\u0643\u0645\u0629 \u062a\u0628\u064a\u0646 \u0644\u0647\u0627 \u0648\u062c\u0648\u062f \u0639\u0642\u062f \u0635\u062d\u064a\u062d \u0648\u0645\u0648\u0642\u0639 \u0628\u064a\u0646 \u0627\u0644\u0637\u0631\u0641\u064a\u0646 \u0648\u062b\u0628\u0648\u062a \u0642\u064a\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u064a \u0628\u062a\u0646\u0641\u064a\u0630 \u0627\u0644\u062a\u0632\u0627\u0645\u0627\u062a\u0647 \u0627\u0644\u062a\u0639\u0627\u0642\u062f\u064a\u0629. \u062d\u0643\u0645\u062a \u0627\u0644\u0645\u062d\u0643\u0645\u0629 \u0628\u0625\u0644\u0632\u0627\u0645 \u0627\u0644\u0645\u062f\u0639\u0649 \u0639\u0644\u064a\u0647 \u0628\u0633\u062f\u0627\u062f \u0645\u0628\u0644\u063a 75000 \u0631\u064a\u0627\u0644 \u0633\u0639\u0648\u062f\u064a"

cls = classify_case(test)
print(f"=== Classification ===")
print(f"Type: {cls['name_en']} confidence={cls['confidence']}")
print(f"Keywords matched: {len(cls['matched_keywords'])}")

pp = extract_legal_principles(test)
print(f"\n=== Legal Principles ===")
print(f"Found: {len(pp)}")
for p in pp:
    print(f"  - {p['name_en']} (section: {p['source_section']}, relevance: {p['relevance']})")

outcome = detect_outcome(test)
amount = extract_compensation_amount(test)
print(f"\n=== Trend Detection ===")
print(f"Outcome: {outcome}")
print(f"Amount: {amount}")

print("\n=== ALL ENGINES OK ===")
