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
                
                new_content = content
                if "$\\rightarrow$" in content or "$\\Rightarrow$" in content or "\\rightarrow" in content:
                    new_content = new_content.replace('$\\rightarrow$', ' → ')
                    new_content = new_content.replace('$\\Rightarrow$', ' ⇒ ')
                    new_content = new_content.replace('\\rightarrow', ' → ')
                    new_content = new_content.replace('\\Rightarrow', ' ⇒ ')
                    
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    count += 1
            except: pass
print(f"Cleaned symbols in {count} files.")
