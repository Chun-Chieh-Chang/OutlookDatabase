import win32com.client
import io
import sys

if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')

def dump_folders(folders, indent=0):
    for f in folders:
        print("  " * indent + f"FOLDER: {f.Name} (Items: {f.Items.Count}, Subfolders: {f.Folders.Count})")
        if f.Folders.Count > 0:
            dump_folders(f.Folders, indent + 1)

for s in outlook.Stores:
    print(f"STORE: {s.DisplayName}")
    try:
        root = s.GetRootFolder()
        dump_folders(root.Folders)
    except Exception as e:
        print(f"  ERROR: {e}")
