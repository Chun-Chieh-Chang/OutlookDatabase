import os
import re

def merge_entities(typo_name, master_name, category="dimensions/spec"):
    wiki_root = 'wiki'
    typo_path = os.path.join(wiki_root, category, f"{typo_name}.md")
    master_path = os.path.join(wiki_root, category, f"{master_name}.md")

    if not os.path.exists(typo_path):
        print(f"Typo file {typo_path} not found.")
        return
    
    print(f"Merging {typo_name} into {master_name}...")
    
    with open(typo_path, 'r', encoding='utf-8-sig') as f:
        typo_content = f.read()
    
    # Extract references (links) from typo content
    refs = re.findall(r'- (\[.*\]\(.*\))', typo_content)
    
    if os.path.exists(master_path):
        with open(master_path, 'r', encoding='utf-8-sig') as f:
            master_content = f.read()
    else:
        master_content = f"# {master_name}\n\n## 📝 自動提取描述\n\n## 🔗 相關引用記錄\n"

    # Append unique refs
    existing_refs = set(re.findall(r'- (\[.*\]\(.*\))', master_content))
    new_refs = [r for r in refs if r not in existing_refs]
    
    if new_refs:
        if "## 相關引用記錄" not in master_content and "## 🔗 相關引用記錄" not in master_content:
            master_content += "\n## 🔗 相關引用記錄\n"
        for r in new_refs:
            master_content += f"- {r}\n"
    
    # Update master file
    with open(master_path, 'w', encoding='utf-8-sig') as f:
        f.write(master_content)
    
    # Remove typo file
    os.remove(typo_path)
    print(f"Successfully merged. {len(new_refs)} new references added.")

if __name__ == "__main__":
    merge_entities("R1-1000", "R1-10000")
