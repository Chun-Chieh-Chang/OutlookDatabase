import os
import json
import random

def run_audit():
    wiki_dir = 'wiki/dimensions/admin'
    with open('scratch/synthesis_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    
    # Randomly sample 10 targets from processed items (1-160)
    processed_targets = targets[:160]
    sample_size = min(10, len(processed_targets))
    samples = random.sample(processed_targets, sample_size)
    
    results = []
    passed = 0
    for s in samples:
        path = s['path']
        status = "FAIL"
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "## 📝 技術描述" in content and len(content) > 600:
                    status = "PASS"
                    passed += 1
        results.append({"name": s['name'], "status": status})
    
    report = {
        "timestamp": str(os.path.getmtime(progress_path)) if os.path.exists(progress_path) else "N/A",
        "sample_size": sample_size,
        "passed": passed,
        "pass_rate": f"{(passed/sample_size)*100}%",
        "details": results
    }
    
    with open('logs/governance_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Audit Complete: {passed}/{sample_size} passed.")

if __name__ == "__main__":
    progress_path = 'logs/progress.json'
    run_audit()
