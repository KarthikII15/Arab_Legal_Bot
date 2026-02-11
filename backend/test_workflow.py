import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def run_workflow():
    print("Starting End-to-End User Journey Validation...\n")
    start_time = time.time()
    
    # 1. Upload & Analyze
    print("[Step 1] Uploading and Analyzing Case...")
    step_start = time.time()
    
    # Simulating a file upload by creating a dummy file content in memory
    # In a real test we'd open a file, but here we can mock the file content
    file_content = """
    الوقائع:
    تعاقد المدعي مع المدعى عليه (شركة مقاولات) لبناء فيلا سكنية بمبلغ 500,000 ريال.
    تأخر المدعى عليه في التسليم لمدة 6 أشهر.
    تسبب التأخير في أضرار للمدعي اضطرته لاستئجار سكن بديل.
    يطلب المدعي فسخ العقد والتعويض.
    
    الأسباب:
    ثبت للمحكمة إخلال المدعى عليه بالتزاماته التعاقدية.
    العقد ينص على غرامة تأخير.
    """
    
    files = {
        'file': ('case_file.txt', file_content, 'text/plain')
    }
    
    try:
        r = requests.post(f"{BASE_URL}/upload-analyze", files=files)
        if r.status_code != 200:
            print(f"Upload Failed: {r.text}")
            return
        analysis = r.json()
        print(f"Analysis Complete in {time.time() - step_start:.2f}s")
        print(f"   - Type: {analysis['classification']['case_type']} (Confidence: {analysis['classification']['confidence']})")
        print(f"   - Recommendation: {analysis['recommendation']['direction']}")
    except Exception as e:
        print(f"Error in Step 1: {e}")
        return

    # 2. Interactive Query Panel
    print("\n[Step 2] Testing Interactive Query Panel (5 Types)...")
    queries = ["outcome", "principles", "similar_cases", "compensation", "confidence"]
    
    for q_type in queries:
        q_start = time.time()
        payload = {"query_type": q_type, "analysis_data": analysis}
        try:
            r = requests.post(f"{BASE_URL}/query", json=payload)
            if r.status_code == 200:
                print(f"   Query '{q_type}' success ({time.time() - q_start:.3f}s)")
            else:
                print(f"   Query '{q_type}' failed: {r.status_code}")
        except Exception as e:
            print(f"   Error querying '{q_type}': {e}")

    # 3. Draft Generation
    print("\n[Step 3] Generating Draft (Plaintiff)...")
    draft_start = time.time()
    
    draft_payload = {
        "case_type": analysis['classification']['case_type'],
        "classification_confidence": analysis['classification']['confidence'],
        "legal_principles": analysis['legal_principles'],
        "recommendation": analysis['recommendation'],
        "party_role": "plaintiff"
    }
    
    try:
        # Note: The /draft endpoint in main.py expects models.
        # But wait, main.py uses Pydantic validaton.
        # When calling via HTTP, we pass JSON. Pydantic on server side parses it.
        # So passing the dicts from 'analysis' JSON response should work perfectly.
        
        r = requests.post(f"{BASE_URL}/draft", json=draft_payload)
        if r.status_code == 200:
            draft = r.json()
            print(f"Draft Generated in {time.time() - draft_start:.2f}s")
            print(f"   - Title: {draft['title']}")
            print(f"   - Length: {len(draft['content'])} characters")
        else:
             print(f"Draft Generation Failed: {r.text}")
    except Exception as e:
        print(f"Error in Step 3: {e}")

    total_time = time.time() - start_time
    print(f"\nWorkflow Validation Complete in {total_time:.2f}s")
    
    if total_time < 5.0:
         print("Performance: EXCELLENT (< 5s)")
    elif total_time < 10.0:
         print("Performance: GOOD (< 10s)")
    else:
         print("Performance: NEEDS OPTIMIZATION (> 10s)")

if __name__ == "__main__":
    run_workflow()
