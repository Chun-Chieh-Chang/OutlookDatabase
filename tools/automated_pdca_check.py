import os
import requests
import sys

# 強制設定輸出為 UTF-8 以支援中文顯示
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_encoding(directory):
    print(f"[SEARCH] Checking encoding consistency: {directory}...")
    errors = 0
    if not os.path.exists(directory):
        print(f"[WARN] Directory {directory} not found.")
        return 0
        
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'rb') as file:
                        raw = file.read()
                        if not raw.startswith(b'\xef\xbb\xbf'):
                            # Check if it's at least valid UTF-8
                            raw.decode('utf-8')
                except Exception:
                    print(f"[ERROR] Encoding Mismatch: {path}")
                    errors += 1
    return errors

def check_api_health():
    print("[SEARCH] Checking API Health (http://127.0.0.1:5000)...")
    endpoints = ['/api/stats', '/api/evolution', '/api/manual']
    all_ok = True
    for ep in endpoints:
        try:
            resp = requests.get(f"http://127.0.0.1:5000{ep}", timeout=5)
            if resp.status_code == 200:
                print(f"[OK] {ep}: Status 200")
            else:
                print(f"[FAIL] {ep}: Status {resp.status_code}")
                all_ok = False
        except Exception as e:
            print(f"[FAIL] {ep}: Connection Error ({e})")
            all_ok = False
    return all_ok

def run_all_checks():
    print("=== SkillsBuilder PDCA Automated Verification v1.1 ===\n")
    
    # 1. Encoding Check
    enc_errors = check_encoding('wiki')
    
    # 2. API Health
    api_ok = check_api_health()
    
    print("\n" + "="*40)
    if enc_errors == 0 and api_ok:
        print("SUCCESS: All anti-regression checks passed. System is ROBUST.")
        sys.exit(0)
    else:
        print("CRITICAL: Regression risks detected. Please perform CAPA immediately.")
        sys.exit(1)

if __name__ == "__main__":
    run_all_checks()
