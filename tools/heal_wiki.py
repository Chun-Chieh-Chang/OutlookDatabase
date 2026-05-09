import os
import shutil
from email_analyzer import EmailAnalyzer

def heal():
    analyzer = EmailAnalyzer()
    wiki_root = 'wiki/dimensions'
    
    # Ensure HR and ADMIN dirs exist
    os.makedirs(os.path.join(wiki_root, 'hr'), exist_ok=True)
    os.makedirs(os.path.join(wiki_root, 'admin'), exist_ok=True)
    
    moved_count = 0
    
    for root, dirs, files in os.walk(wiki_root):
        current_cat = os.path.basename(root)
        for f in files:
            if not f.endswith('.md'): continue
            
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Rule-based fast track (The "104 Defense")
            hr_keywords = ['招募', '徵才', '104', '薪資', '福利', '面試', '履歷', '投遞']
            if any(k in content or k in f for k in hr_keywords):
                target_cat = 'hr'
            elif any(k in content for k in ['會議記錄', '通知', '快遞']):
                target_cat = 'admin'
            else:
                # Keep as is unless it is obviously wrong
                target_cat = current_cat
                
            if target_cat != current_cat:
                target_dir = os.path.join(wiki_root, target_cat)
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(path, os.path.join(target_dir, f))
                print(f"Moved {f} from {current_cat} -> {target_cat}")
                moved_count += 1

    # Cleanup empty dirs
    for root, dirs, files in os.walk(wiki_root, topdown=False):
        if not dirs and not files:
            os.rmdir(root)
            print(f"Removed empty dir: {root}")

    print(f"Heal complete. Total entities relocated: {moved_count}")

if __name__ == '__main__':
    heal()
