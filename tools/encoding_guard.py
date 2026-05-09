import sys
import io

def enforce_safe_encoding():
    """
    強制執行安全編碼輸出。
    自動偵測終端編碼，並對無法顯示的字元進行過濾 (replace 模式)。
    """
    # 如果是 Windows 且編碼不是 utf-8 (通常是 cp950)
    if sys.stdout.encoding.lower() != 'utf-8':
        # 重新包裝 stdout，遇到非法字元時使用 '?' 替代而非報錯
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding=sys.stdout.encoding, 
            errors='replace'
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding=sys.stderr.encoding, 
            errors='replace'
        )

# 當這個模組被 import 時自動執行
enforce_safe_encoding()

def safe_print(*args, **kwargs):
    """
    包裝過的 print，確保萬無一失。
    """
    new_args = []
    for arg in args:
        if isinstance(arg, str):
            # 雖然已有 sys.stdout 的保護，但這裡再做一次顯式過濾
            # 只保留 BMP 內的字元 (過濾 Emoji)
            safe_str = "".join(c for c in arg if ord(c) <= 0xFFFF)
            new_args.append(safe_str)
        else:
            new_args.append(arg)
    print(*new_args, **kwargs)

if __name__ == "__main__":
    # 測試代碼：即使包含 Emoji 也不會崩潰
    enforce_safe_encoding()
    print("Test: This contains an emoji 🚀 and should NOT crash.")
    safe_print("SafeTest: This contains 🚀 and will strip it.")
