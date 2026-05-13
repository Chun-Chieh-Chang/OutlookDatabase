import json
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

def semantic_tiering():
    with open('scratch/synthesis_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    
    # Process in batches of 30 to save time
    batch_size = 30
    l1_targets = []
    
    print(f"Starting Semantic Audit for {len(targets)} entities...")
    
    for i in range(0, len(targets), batch_size):
        batch = [t['name'] for t in targets[i:i+batch_size]]
        print(f"Auditing Batch {i//batch_size + 1}...")
        
        prompt = f"""你是一位資深工業數據治理專家。請從以下列表中挑選出具備「高價值」的實體。
高價值定義：涉及零件編號(R1/B/712等)、品質異常(不良/洩漏/損壞)、技術變更(SCN/變更)、客訴(RMA/抱怨)、稽核(Audit/ISO)或關鍵專案。
請僅回覆符合要求的名稱，每行一個，不要有額外解釋。

列表：
{batch}
"""
        try:
            result = subprocess.run(['ollama', 'run', 'llama3.2', prompt], capture_output=True, text=True, encoding='utf-8')
            high_value_names = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            for t in targets[i:i+batch_size]:
                if t['name'] in high_value_names:
                    t['tier'] = 'L1'
                    l1_targets.append(t)
                else:
                    t['tier'] = 'L2'
        except:
            # Fallback to literal if AI fails
            pass

    with open('scratch/synthesis_targets_tiered.json', 'w', encoding='utf-8') as f:
        json.dump(targets, f, indent=2, ensure_ascii=False)
        
    print(f"Semantic Tiering Complete: {len(l1_targets)} L1 entities identified.")

if __name__ == "__main__":
    semantic_tiering()
