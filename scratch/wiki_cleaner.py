import os

def fix_encoding(directory):
    encodings = ['utf-8-sig', 'utf-8', 'cp950', 'big5']
    count = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                content = None
                # Try reading with fallback
                for enc in encodings:
                    try:
                        with open(path, 'r', encoding=enc) as file:
                            content = file.read()
                        break
                    except:
                        continue
                
                if content:
                    # Write back as perfect utf-8-sig
                    with open(path, 'w', encoding='utf-8-sig') as file:
                        file.write(content)
                    count += 1
    print(f"Cleaned {count} Wiki files.")

if __name__ == "__main__":
    fix_encoding('wiki')
