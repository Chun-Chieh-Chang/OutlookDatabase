import json
import re

def comprehensive_tiering():
    with open('scratch/synthesis_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    
    # 擴展開發者級別的工業關鍵字庫 (模擬語意)
    patterns = [
        r'r1-', r'b-', r'v1-', r'712-', r'mold', r'defect', r'leak', r'complaint', r'audit', r'iso',
        r'change', r'scn', r'fai', r'rma', r'tolerance', r'drawing', r'spec', r'quality',
        r'validation', r'verification', r'oqa', r'iqc', r'pqc', r'capa', r'car', r'ncr',
        r'不良', r'變更', r'稽核', r'客訴', r'模具', r'洩漏', r'損壞', r'尺寸', r'驗證', r'規格',
        r'批號', r'lot', r'pn', r'po', r'樣品', r'sample', r'滅菌', r'sterile', r'漏料', r'機台', r'維修'
    ]
    regex = re.compile('|'.join(patterns), re.IGNORECASE)
    
    l1 = []
    l2 = []
    for t in targets:
        if regex.search(t['name']):
            t['tier'] = 'L1'
            l1.append(t)
        else:
            t['tier'] = 'L2'
            l2.append(t)
            
    with open('scratch/synthesis_targets_tiered.json', 'w', encoding='utf-8') as f:
        json.dump(targets, f, indent=2, ensure_ascii=False)
        
    print(f"Comprehensive Tiering Complete!")
    print(f"🔥 L1 (Industrial Assets): {len(l1)}")
    print(f"💤 L2 (Others): {len(l2)}")

if __name__ == "__main__":
    comprehensive_tiering()
