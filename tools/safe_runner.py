import os
import subprocess
import tempfile
import sys

def run_safe_python(code_snippet, description="Safe Runner Task"):
    """
    接收 Python 代碼片段，寫入暫存檔並執行，徹底規避 Shell 轉義問題。
    """
    # 強制加入編碼與路徑防護
    header = f"""
import sys, os
import io
# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.getcwd())
try:
    import tools.encoding_guard
except:
    pass

print(f"--- Executing: {description} ---")
"""
    full_code = header + code_snippet
    
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as tmp:
        tmp.write(full_code)
        tmp_path = tmp.name
        
    try:
        # 使用當前 Python 解析器執行
        result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error executing snippet:\n{result.stderr}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    # 測試：包含複雜引號與符號的代碼
    test_code = "print('Success: This handled \"quotes\" and % signs correctly.')"
    run_safe_python(test_code, "Encoding & Escape Test")
