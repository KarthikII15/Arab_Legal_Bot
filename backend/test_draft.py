import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_draft_endpoint():
    print("Testing /draft endpoint...")
    
    # Mock data based on a successful analysis
    payload = {
        "case_type": "Commercial Dispute",
        "classification_confidence": 0.95,
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
        "recommendation": {
            "recommendation_ar": "نوصي بالمطالبة بالتعويض",
            "recommendation_en": "Recommend claiming details",
            "direction": "plaintiff_likely",
            "confidence": 0.8,
            "disclaimer_ar": "disclaimer",
            "disclaimer_en": "disclaimer",
            "based_on_sample_size": 5,
            "reliability": "high"
        },
        "party_role": "plaintiff"
    }

    try:
        r = requests.post(f"{BASE_URL}/draft", json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("PASS")
            print(f"Title: {data['title']}")
            print(f"Content preview: {data['content'][:100]}...")
        else:
            print(f"FAIL: {r.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_draft_endpoint()
