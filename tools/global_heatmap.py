import os
import sqlite3
import json
import re
from datetime import datetime

# Import encoding guard for stability
import sys
sys.path.append(os.getcwd())
try:
    import tools.encoding_guard
except:
    pass

def global_quality_heatmap():
    print("Starting Global Quality Heatmap analysis...")
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    
    # 1. 識別高頻詞 (假設 3 個字以上且與品質相關)
    # 我們先從我們已知的 8 大維度關鍵字入手
    keywords = ['黑點', '毛邊', '縮水', '尺寸', '超差', 'NG', '異常', '退貨', '修模', '客訴']
    
    # 2. 統計各關鍵字在不同月份的分布
    heatmap_data = {}
    
    for kw in keywords:
        cursor.execute("""
            SELECT substr(received_time, 1, 7) as month, COUNT(*) 
            FROM emails 
            WHERE body LIKE ? OR subject LIKE ? 
            GROUP BY month 
            ORDER BY month ASC
        """, (f'%{kw}%', f'%{kw}%'))
        rows = cursor.fetchall()
        heatmap_data[kw] = {r[0]: r[1] for r in rows}
        
    # 3. 識別潛在的高風險專案 (從主旨中提取 [XXXX] 格式或連續大寫字母)
    cursor.execute("SELECT subject FROM emails WHERE subject LIKE '%RE:%' OR subject LIKE '%FW:%'")
    subjects = cursor.fetchall()
    project_patterns = {}
    for (sub,) in subjects:
        # 尋找中括號內的專案名或連續的料號特徵
        matches = re.findall(r'\[(.*?)\]', sub)
        for m in matches:
            if len(m) < 20: # 避免抓到太長的句子
                project_patterns[m] = project_patterns.get(m, 0) + 1
                
    sorted_projects = sorted(project_patterns.items(), key=lambda x: x[1], reverse=True)[:15]

    # 4. 產出全局報告
    report_path = 'wiki/dimensions/qms/Global_Quality_Heatmap.md'
    
    md = f"""---
title: 全局品質熱力圖 (QC 3.0)
category: qms
tags: ["#全局分析", "#熱力圖", "#風險預警"]
updated: {datetime.now().strftime('%Y-%m-%d')}
---

# Global Quality Heatmap (全局品質熱力圖)

## 📊 異常關鍵字趨勢 (Anomaly Trends)
以下是近期最高頻的品質異常關鍵字分布：

"""
    # 建立 Markdown 表格
    months = sorted(list(set([m for kw in heatmap_data for m in heatmap_data[kw]])))[-6:] # 只取最近 6 個月
    md += "| 關鍵字 | " + " | ".join(months) + " |\n"
    md += "| :--- | " + " | ".join(["---"] * len(months)) + " |\n"
    
    for kw in keywords:
        row = f"| {kw} | "
        for m in months:
            count = heatmap_data[kw].get(m, 0)
            status = "🔥" if count > 10 else ("⚠️" if count > 5 else "✅")
            # 移除 Emoji 以符合禁令，改用文字標籤
            status_text = "[HIGH]" if count > 10 else ("[WARN]" if count > 5 else "[OK]")
            row += f"{count} {status_text} | "
        md += row + "\n"
        
    md += "\n## 🏭 活躍專案排行 (Top Active Projects)\n"
    md += "| 專案識別 | 討論熱度 (郵件數) | 狀態 |\n"
    md += "| :--- | :--- | :--- |\n"
    for proj, count in sorted_projects:
        md += f"| [[{proj}]] | {count} | [Active] |\n"
        
    md += "\n## 🛡️ 戰略建議\n"
    md += "1. **集中火力**：應優先針對 [HIGH] 標籤密集的月份與關鍵字進行專案回溯。\n"
    md += "2. **閉環檢查**：對排名靠前的活躍專案進行 NCA/CAPA 完整性稽核。\n"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md)
        
    conn.close()
    print(f"Heatmap report generated at: {report_path}")

if __name__ == "__main__":
    global_quality_heatmap()
