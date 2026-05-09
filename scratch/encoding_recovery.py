import os
import sys
import io

# Fix terminal encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def try_recover(path):
    print(f"--- Attempting to recover: {path} ---")
    try:
        # 1. Read the corrupted file (which was written as UTF-8)
        with open(path, 'r', encoding='utf-8') as f:
            corrupted_str = f.read()
        
        # 2. Reverse the PowerShell mistake:
        # PowerShell read original UTF-8 bytes and thought they were CP950.
        # We need to turn those characters back into the bytes they represent in CP950.
        try:
            raw_bytes = corrupted_str.encode('cp950', errors='ignore')
            recovered_str = raw_bytes.decode('utf-8', errors='ignore')
            
            # 3. Success check: check if common keywords are back
            if "SkillsBuilder" in recovered_str or "Architecture" in recovered_str or "核心" in recovered_str:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    f.write(recovered_str)
                print(f"SUCCESS: {path} has been restored.")
                return True
            else:
                print(f"FAILED: Keywords not found in recovered text for {path}")
        except Exception as e:
            print(f"ERROR during byte conversion for {path}: {e}")
            
    except Exception as e:
        print(f"FATAL ERROR for {path}: {e}")
    return False

files_to_fix = [
    'CORE_ARCHITECTURE.md',
    'SYSTEM_MANUAL.md',
    'DEV_LOG.md'
]

for f in files_to_fix:
    if os.path.exists(f):
        try_recover(f)
