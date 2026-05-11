import win32com.client
import io
import sys

if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
for s in outlook.Stores:
    print(f"STORE: {s.DisplayName}")
    try:
        root = s.GetRootFolder()
        for f in root.Folders:
            print(f"  FOLDER: {f.Name} (Items: {f.Items.Count})")
            # Scan one level deeper
            try:
                for sub in f.Folders:
                    print(f"    SUBFOLDER: {sub.Name} (Items: {sub.Items.Count})")
            except: pass
    except Exception as e:
        print(f"  ERROR: {e}")
