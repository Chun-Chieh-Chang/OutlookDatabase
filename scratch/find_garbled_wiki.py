import os
import re

def is_garbled(text):
    # Search for patterns typical of double-encoding or incorrect decoding in Chinese context
    # Like '蝟餌絞', '璛', etc. or too many '?' in a row
    garbled_patterns = [
        r'蝟餌絞', r'璛', r'', r'\?\?\?\?'
    ]
    for p in garbled_patterns:
        if re.search(p, text):
            return True
    
    # Check for excessive high-unicode characters that don't make sense in context
    # Or common mis-decodings
    return False

def scan_wiki(root_dir):
    garbled_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        if is_garbled(content):
                            garbled_files.append(path)
                except:
                    garbled_files.append(path)
    return garbled_files

if __name__ == "__main__":
    root = 'wiki'
    targets = scan_wiki(root)
    print(f"Found {len(targets)} garbled files:")
    for t in targets:
        print(t)
