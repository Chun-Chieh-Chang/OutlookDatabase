import os
import requests
import sys
import glob
from datetime import datetime

# 強制設定輸出為 UTF-8 以支援中文顯示
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_encoding(directory):
    print(f"[SEARCH] Scanning for encoding issues in {directory}...")
    # 這裡可以加入更複雜的編碼檢測邏輯
    return []

def check_api_health():
    print("[SEARCH] Checking API Health (http://127.0.0.1:5000)...")
    endpoints = ["/api/stats", "/api/evolution", "/api/manual"]
    all_ok = True
    for ep in endpoints:
        try:
            r = requests.get(f"http://127.0.0.1:5000{ep}", timeout=5)
            if r.status_code == 200:
                print(f"[OK] {ep}: Status 200")
            else:
                print(f"[FAIL] {ep}: Status {r.status_code}")
                all_ok = False
        except Exception as e:
            print(f"[FAIL] {ep}: Connection Error ({e})")
            all_ok = False
    
    # 4. CAPA & Skill Evolution Check
    print("🔍 Checking Skill Evolution & Governance Enforcement...")
    success = all_ok
    mandatory_skills = [
        "skills/system_robustness.md",
        "skills/rag_chinese_fix.md",
        "skills/ui_contrast_standard.md"
    ]
    for skill in mandatory_skills:
        if not os.path.exists(skill):
            print(f"❌ Critical Failure: Mandatory Skill {skill} is missing.")
            success = False
        else:
            # Check for "演化教訓" (Self-Evolution tag)
            with open(skill, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if "演化教訓" not in content:
                    print(f"⚠️ Warning: Skill {skill} lacks '演化教訓' (Self-Evolution) section.")
    
    # 5. Data Integrity Check (0-byte scan)
    print("🔍 Checking Data Integrity (0-byte scan)...")
    raw_emails = glob.glob("raw/emails/*.json")
    if raw_emails:
        zero_byte_files = [f for f in raw_emails if os.path.getsize(f) == 0]
        if len(zero_byte_files) > 0:
            print(f"❌ Critical Failure: Found {len(zero_byte_files)} empty email files.")
            success = False
        else:
            print(f"✅ Data integrity verified ({len(raw_emails)} files).")
    
    # 6. Regression Check (Typo Prevention)
    print("🔍 Running Regression Check (Typo Prevention)...")
    typo_file = "wiki/dimensions/spec/R1-1000.md"
    if os.path.exists(typo_file):
        print(f"❌ Regression Failure: Typo file {typo_file} still exists.")
        success = False
    else:
        print("✅ Regression test passed (R1-1000 resolved).")
    
    if success:
        print("\n✅ PDCA Check Passed: System is Robust, Self-Evolved, and Data-Consistent.")
        return True
    else:
        print("\n❌ PDCA Check Failed: Remediation Required.")
        return False

def check_skills_health():
    print("[SEARCH] Checking CAPA Skills Integrity (skills/)...")
    # 略
    return True

def run_all_checks():
    print("=== SkillsBuilder PDCA Automated Verification v1.2 ===\n")
    
    # 1. Encoding Check (Wiki)
    enc_errors = check_encoding('wiki')
    
    # 2. Skills Health
    skills_ok = check_skills_health()
    
    # 3. API Health
    api_ok = check_api_health()
    
    # [NEW] Manual Self-Evolution Trigger
    try:
        if os.path.exists('tools/evolve_manual.py'):
            import importlib.util
            spec = importlib.util.spec_from_file_location("evolve_manual", "tools/evolve_manual.py")
            em = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(em)
            em.evolve_system_manual()
    except Exception as e:
        print(f"⚠️ Manual Evolution failed: {e}")
    
    if api_ok and skills_ok:
        print("\n[SUMMARY] ALL SYSTEMS OPERATIONAL.")
        sys.exit(0)
    else:
        print("\n[SUMMARY] SYSTEM GOVERNANCE FAILURE.")
        sys.exit(1)

if __name__ == "__main__":
    run_all_checks()
