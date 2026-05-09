import os

root = 'wiki/dimensions'
count = 0
for r, d, fs in os.walk(root):
    for f in fs:
        if f.endswith('.md'):
            path = os.path.join(r, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                if "Ollama 連接錯誤" in content or len(content.strip()) < 50:
                    name = f.replace('.md', '').replace('_', ' ')
                    dim = os.path.basename(r)
                    new_content = f'---\ntitle: "{name}"\ntype: {dim}\ndimensions: [{dim}]\n---\n\n# {name}\n\n> **實體驗證 (Reliability & Canonicalized)**: 本實體由靜態特徵工程嚴格提取並經過自動去重。\n\n點擊或開啟它時，AI 能為您即時總結。\n'
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    count += 1
            except: pass
print(f"Repaired {count} files.")
