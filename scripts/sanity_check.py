import re
import os
import sys

def check_html_standards(content):
    errors = []
    # 檢查是否含有內聯樣式 (簡單判斷 style=")
    if 'style="' in content:
        # 排除必要的動態樣式 (如 animation-delay)
        if not re.search(r'style="[^"]*animation-delay', content):
            errors.append("❌ 發現內聯樣式：請將其移動到 <style> 區塊或使用 CSS 變數。")
    
    # 檢查是否含有重複的 ID
    ids = re.findall(r'id="([^"]+)"', content)
    if len(ids) != len(set(ids)):
        duplicates = [x for x in ids if ids.count(x) > 1]
        errors.append(f"❌ 發現重複的 ID: {set(duplicates)}")
        
    return errors

def check_js_standards(content):
    errors = []
    # 檢查是否繞過 UI Helper 直接使用 getElementById
    if 'document.getElementById' in content and 'const UI =' not in content:
        # 允許在 UI 對象定義內部使用
        if not re.search(r'get: \(id\) => document\.getElementById\(id\)', content):
             errors.append("❌ 發現直接使用 getElementById：請統一透過 UI.get(id) 操作。")
             
    # 檢查是否缺少防禦性檢查
    if '.innerHTML =' in content and 'if(' not in content:
        errors.append("⚠️ 發現不安全的 innerHTML 寫入：請確保有先檢查元素是否存在。")
        
    return errors

def check_python_standards(content):
    errors = []
    # 檢查是否含有未清洗的 'Unknown' 字串
    if "'Unknown'" in content or '"Unknown"' in content:
        if "/api/stats" in content or "recent_emails" in content:
            errors.append("❌ 發現硬編碼的 'Unknown'：請確保使用發件人清洗邏輯 (Fallback 鏈路)。")
            
    return errors

def run_sanity_check():
    files_to_check = {
        'templates/index.html': check_html_standards,
        'static/js/main.js': check_js_standards,
        'web_app.py': check_python_standards
    }
    
    all_clear = True
    print("[LOG] Starting SkillsBuilder Code Sanity Check...")
    
    for file_path, check_func in files_to_check.items():
        if not os.path.exists(file_path): continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            errors = check_func(content)
            if errors:
                all_clear = False
                print(f"\n[FILE] {file_path}")
                for err in errors:
                    print(err.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
                    
    if all_clear:
        print("\n[SUCCESS] All checks passed! Code adheres to flagship standards.")
    else:
        print("\n[FAIL] Sanity check failed. Please fix the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    run_sanity_check()
