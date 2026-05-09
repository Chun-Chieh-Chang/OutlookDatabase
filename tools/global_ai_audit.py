import os
import shutil
import json
import re
from email_analyzer import EmailAnalyzer

def audit():
    print("🧠 Starting Global AI Audit (v2.0) for 100% Accuracy...")
    analyzer = EmailAnalyzer()
    wiki_root = 'wiki/dimensions'
    
    # Categories to check
    valid_categories = ['iqc', 'pqc', 'oqc', 'capa', 'nca', 'spec', 'machine', 'man', 'material', 'method', 'environment', 'qms', 'msa', 'supplier', 'client', 'project', 'audit', 'hr', 'admin', 'event']
    
    # Stats
    total = 0
    moved = 0
    errors = 0
    
    # Collect all files first to avoid iterator issues during move
    all_files = []
    for root, dirs, files in os.walk(wiki_root):
        cat = os.path.basename(root)
        for f in files:
            if f.endswith('.md'):
                all_files.append((os.path.join(root, f), cat, f))
    
    print(f"📦 Found {len(all_files)} nodes to audit.")

    for path, current_cat, filename in all_files:
        total += 1
        print(f"[{total}/{len(all_files)}] Auditing: {filename}...", end='\r')
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract content without frontmatter for better AI focus
            clean_content = re.sub(r'---.*?---', '', content, flags=re.DOTALL)
            
            # Call AI for classification
            res = analyzer.extract_wiki_entities(subject=filename, body=clean_content)
            
            if res.get('dimensions'):
                ai_cat = res['dimensions'][0].get('category', 'event').lower()
                
                # Normalize AI cat
                if ai_cat not in valid_categories:
                    ai_cat = 'event'
                
                if ai_cat != current_cat:
                    target_dir = os.path.join(wiki_root, ai_cat)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Update content's category tag
                    new_content = content.replace(f"category: {current_cat}", f"category: {ai_cat}")
                    new_content = new_content.replace(f"type: {current_cat}", f"type: {ai_cat}")
                    
                    target_path = os.path.join(target_dir, filename)
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                        
                    shutil.move(path, target_path)
                    print(f"\n✅ RECLASSIFIED: {filename} ({current_cat} -> {ai_cat})")
                    moved += 1
            
        except Exception as e:
            print(f"\n❌ Error auditing {filename}: {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Audit Session Complete:")
    print(f"  Total Audited: {total}")
    print(f"  Reclassified: {moved}")
    print(f"  Errors: {errors}")
    print(f"{'='*50}")

if __name__ == '__main__':
    audit()
