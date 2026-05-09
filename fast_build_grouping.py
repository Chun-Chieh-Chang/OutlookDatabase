import sqlite3
import re
import os
import glob

def clean_entity(name):
    name = re.sub(r'\s+', ' ', str(name))
    name = re.sub(r'[\\/*?:"<>|\'~`]', '', name)
    return name.strip()

def canonicalize(dim, name):
    name = name.strip()
    if dim == 'man':
        # Deduplication for names: abbie.tai -> Abbie Tai, abbie_tai -> Abbie Tai
        name = name.replace('.', ' ').replace('_', ' ')
        name = ' '.join([w.capitalize() for w in name.split()])
    elif dim == 'projects':
        name = re.sub(r'^PROJECT\s+', '', name, flags=re.IGNORECASE).strip()
    elif dim == 'spec':
        # E.g. R1-10134 and R1-10134A -> typically keep distinct if it's a rev, but standardize
        name = name.upper()
    return name

def build():
    # 1. CLEANUP PREVIOUS STATIC GENERATIONS TO PREVENT ORPHANS
    print("Cleaning up old auto-generated static files...")
    cleaned = 0
    for root, _, files in os.walk('wiki/dimensions'):
        for f in files:
            if f.endswith('.md') and f != 'index.md':
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    if "靜態正則表達式快速提取" in content or "靜態特徵工程" in content:
                        os.remove(path)
                        cleaned += 1
                except:
                    pass
    print(f"Cleaned {cleaned} orphan auto-generated files.")

    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    
    entities_found = {
        "man": {},
        "organizations": {},
        "projects": {},
        "spec": {},
        "pqc": {},
        "hr": {}
    }
    
    print("Extracting MAN (Senders) via DB aggregation...")
    cursor.execute("SELECT sender_name, COUNT(*) FROM emails WHERE sender_name IS NOT NULL AND sender_name != '' GROUP BY sender_name HAVING COUNT(*) >= 5")
    for row in cursor:
        sender = clean_entity(row[0])
        if sender and len(sender) > 1 and len(sender) < 40 and sender.lower() != 'unknown' and '@' not in sender:
            # Canonicalize
            sender = canonicalize('man', sender)
            entities_found['man'][sender] = entities_found['man'].get(sender, 0) + row[1]

    print("Extracting ORGANIZATIONS via email domains...")
    cursor.execute("SELECT sender_email FROM emails WHERE sender_email IS NOT NULL AND sender_email != ''")
    for row in cursor:
        email = row[0]
        if email and '@' in email:
            domain = email.split('@')[1].split('.')[0].upper()
            domain = clean_entity(domain)
            if len(domain) > 2 and domain not in ['GMAIL', 'HOTMAIL', 'YAHOO', 'OUTLOOK', 'HINET', 'MSN', 'ICLOUD']:
                entities_found['organizations'][domain] = entities_found['organizations'].get(domain, 0) + 1

    print("Extracting SPEC, PQC, PROJECTS via Regex scanning...")
    cursor.execute("SELECT entry_id, subject, body FROM emails")
    
    rules = {
        "projects": [
            re.compile(r'\b(QIP[0-9]*|PDCA|NPI|MP|EVT|DVT|PVT|RMA|FACA)\b', re.IGNORECASE),
            re.compile(r'\b(Project\s+[A-Z0-9]+)\b', re.IGNORECASE)
        ],
        "spec": [
            re.compile(r'\b[A-Z]{1,3}\d{1,2}-\d{4,6}[A-Z]*\b', re.IGNORECASE),
            re.compile(r'\b[0-9]{3,5}-[A-Z0-9]{4,8}\b', re.IGNORECASE)
        ],
        "pqc": [
            re.compile(r'\b(CAPA|NCA|CAR|8D|SCAR|OQC|IQC|IPQC)\b', re.IGNORECASE),
            re.compile(r'\b(CPK|PPK|SPC|Yield|Defect|Failure|RCA)\b', re.IGNORECASE)
        ],
        "hr": [
            re.compile(r'\b(Leave|Vacation|Overtime|Training|KPI|Review|Interview)\b', re.IGNORECASE)
        ]
    }
    
    count = 0
    for row in cursor:
        entry_id, subject, body = row
        text = (subject or "") + " " + (body or "")
        count += 1
        
        for dim, compiled_rules in rules.items():
            for regex in compiled_rules:
                for match in regex.finditer(text):
                    raw_match = match.group()
                    m = clean_entity(raw_match).upper()
                    
                    if len(m) < 2 or len(m) > 25:
                        continue
                        
                    m = canonicalize(dim, m)
                    entities_found[dim][m] = entities_found[dim].get(m, 0) + 1
                    
        if count % 5000 == 0:
            print(f"Scanned {count} emails for text patterns...")

    conn.close()
    
    print(f"Total scanned: {count} emails.")
    total_created = 0
    
    for dim, entities in entities_found.items():
        dim_dir = f"wiki/dimensions/{dim}"
        os.makedirs(dim_dir, exist_ok=True)
            
        for ent, freq in entities.items():
            threshold = 3 if dim == 'spec' else 5
            if freq >= threshold:
                safe_name = re.sub(r'[^a-zA-Z0-9_\-\u4e00-\u9fa5]', '_', ent)
                file_path = f"{dim_dir}/{safe_name}.md"
                # Preserve existing files that weren't auto-generated
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"---\ntitle: \"{ent}\"\ntype: {dim}\ndimensions: [{dim}]\n---\n\n")
                        f.write(f"# {ent}\n\n")
                        f.write(f"> **實體驗證 (Reliability & Canonicalized)**: 本實體由靜態特徵工程嚴格提取並經過自動去重。\n\n")
                        f.write(f"歷史郵件出現次數: **{freq} 次**。點擊或開啟它時，AI 能為您即時總結。\n")
                    total_created += 1
                    
    print(f"Created/Updated {total_created} knowledge entity files comprehensively.")

if __name__ == '__main__':
    build()
