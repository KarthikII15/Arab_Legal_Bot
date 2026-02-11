import requests

BASE_URL = "http://127.0.0.1:5000"

def test_upload_txt():
    print("Testing /upload with TXT...")
    # Create a dummy file in memory
    files = {'file': ('test.txt', 'This is a test case text for upload.', 'text/plain')}
    try:
        r = requests.post(f"{BASE_URL}/upload", files=files)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
             print("PASS")
             print(f"Response text: {r.json().get('text')}")
        else:
             print(f"FAIL: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_upload_analyze_txt():
    print("\nTesting /upload-analyze with TXT...")
    text = "الوقائع: تقدم المدعي بدعوى يطالب فيها بمبلغ 5000 ريال. الأسباب: ثبت للدائرة صحة الدعوى. الحكم: إلزام المدعى عليه بالمبلغ."
    files = {'file': ('case.txt', text.encode('utf-8'), 'text/plain')}
    try:
        r = requests.post(f"{BASE_URL}/upload-analyze", files=files)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if 'classification' in data:
                print("PASS")
                print(f"Classification: {data['classification']['name_en']}")
            else:
                 print("FAIL: Missing classification")
        else:
            print(f"FAIL: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload_txt()
    test_upload_analyze_txt()
