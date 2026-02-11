import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_query_endpoint():
    print("Testing /query endpoint...")
    
    # Mock analysis data
    analysis_data = {
        "classification": {
            "case_type": "Commercial",
            "name_ar": "نزي تجاري",
            "name_en": "Commercial Dispute",
            "confidence": 0.9,
            "matched_keywords": [],
            "sub_types": []
        },
        "legal_principles": [
            {
                "id": "p1",
                "name_ar": "العقد شريعة المتعاقدين",
                "name_en": "P1",
                "description_ar": "desc",
                "source_section": "reasoning",
                "evidence": "text",
                "relevance": 1.0,
                "match_count": 1
            }
        ],
        "trends": {
            "outcomes": {"plaintiff_win": 5, "plaintiff_loss": 2},
            "plaintiff_win_rate": 71.4,
            "average_compensation": 50000.0,
            "median_compensation": 40000.0,
            "compensation_range": {"min": 1000, "max": 100000},
            "compensation_count": 5,
            "sample_size": 7,
            "decided_cases": 7,
            "reliability": "high"
        },
        "recommendation": {
            "recommendation_ar": "نوصي بالمطالبة بالتعويض",
            "recommendation_en": "Recommend claiming details",
            "direction": "plaintiff_likely",
            "confidence": 0.8,
            "disclaimer_ar": "disclaimer",
            "disclaimer_en": "disclaimer",
            "supporting_principles": [],
            "based_on_sample_size": 7,
            "reliability": "high"
        }
    }

    # Test 1: Outcome
    print("\n[1] Testing 'outcome' query...")
    payload1 = {"query_type": "outcome", "analysis_data": analysis_data}
    try:
        r = requests.post(f"{BASE_URL}/query", json=payload1)
        if r.status_code == 200:
            print("PASS: Outcome received.")
            print(f"Data keys: {r.json().get('data', {}).keys()}")
        else:
            print(f"FAIL: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Compensation
    print("\n[2] Testing 'compensation' query...")
    payload2 = {"query_type": "compensation", "analysis_data": analysis_data}
    try:
        r = requests.post(f"{BASE_URL}/query", json=payload2)
        if r.status_code == 200:
            print("PASS: Compensation received.")
            # print(r.json()['answer']) # Skip printing Arabic to avoid charmap error
        else:
            print(f"FAIL: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_query_endpoint()
