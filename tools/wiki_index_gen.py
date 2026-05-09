import os
import json
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKI_DIR = 'wiki'
DIMENSIONS_DIR = os.path.join(WIKI_DIR, 'dimensions')
INDEX_FILE = os.path.join(WIKI_DIR, 'index.md')

# Nice labels for known dimensions
LABEL_MAP = {
    'man': '👤 人員 (Man) - 權責與通訊網絡',
    'machine': '⚙️ 機器 (Machine) - 設備與工具',
    'material': '📦 物料 (Material) - 零件與產品',
    'method': '📜 方法 (Method) - SOP 與工藝',
    'environment': '🌍 環境 (Environment) - 場域',
    'measurement': '📏 測量 (Measurement) - 數據與檢驗',
    'hr': '👥 人力資源 (HR) - 招聘與組織',
    'pqc': '🔍 製程品管 (PQC) - 現場品質',
    'qms': '🛡️ 品質體系 (QMS) - 標準與驗證',
    'spec': '📋 規格與標準 (Spec) - 技術要求',
    'admin': '📁 行政管理 (Admin)',
    'events': '📅 事件與里程碑 (Events)',
    'projects': '🏗️ 專案體系 (Projects)',
    'organizations': '🏢 組織與廠商 (Organizations)',
    'artifacts': '📄 交付物與報告 (Artifacts)',
    'domains': '🧪 技術領域 (Domains)'
}

def generate_index():
    print("📋 Generating Multi-dimensional Wiki Index...")
    
    graph_stats = {"node_count": 0, "edge_count": 0, "updated": "N/A"}
    alias_count = 0
    graph_store_path = os.path.join(WIKI_DIR, 'graph_store.json')
    alias_registry_path = os.path.join(WIKI_DIR, '.alias_registry.json')
    
    if os.path.exists(graph_store_path):
        try:
            with open(graph_store_path, 'r', encoding='utf-8') as gf:
                gs = json.load(gf)
                graph_stats = gs.get("meta", graph_stats)
        except: pass
    
    if os.path.exists(alias_registry_path):
        try:
            with open(alias_registry_path, 'r', encoding='utf-8') as af:
                alias_count = len(json.load(af))
        except: pass
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write("# SkillsBuilder 工業知識圖譜 (Multi-dimensional Knowledge Graph)\n\n")
        f.write("> 本索引整合「核心治理」、「資源維度」、「品質體系」與「生命週期」，提供全方位工業決策支援。\n\n")
        
        # Stats
        f.write("## 📊 知識規模統計\n")
        f.write(f"| 指標 | 數值 |\n| :--- | :--- |\n")
        f.write(f"| 知識節點 (Nodes) | {graph_stats.get('node_count', 0)} |\n")
        f.write(f"| 關聯強度 (Edges) | {graph_stats.get('edge_count', 0)} |\n")
        f.write(f"| 別名註冊 (Aliases) | {alias_count} |\n")
        f.write(f"| 最後進化時間 | {graph_stats.get('updated', 'N/A')[:19]} |\n\n")
        
        # Auto-discover Dimensions
        f.write("## 🏛️ 多維度知識導航 (Knowledge Navigation)\n")
        
        if os.path.exists(DIMENSIONS_DIR):
            dims = sorted(os.listdir(DIMENSIONS_DIR))
            for dim in dims:
                dim_path = os.path.join(DIMENSIONS_DIR, dim)
                if not os.path.isdir(dim_path): continue
                
                files = [file for file in os.listdir(dim_path) if file.endswith('.md')]
                if not files: continue
                
                label = LABEL_MAP.get(dim, f"📂 {dim.upper()}")
                f.write(f"### {label}\n")
                for filename in sorted(files):
                    name = filename.replace('.md', '')
                    f.write(f"* [{name}](dimensions/{dim}/{filename})\n")
                f.write("\n")
                
        # Lifecycle View
        f.write("## 🔄 管理週期 (PDCA/CAPA View)\n")
        # ... (Simplified for Index)
        f.write("* [查看生命週期視圖](lifecycle/plan/)\n")
        f.write("* [查看改善措施視圖](improvement/problem/)\n")
            
    print(f"✅ Index generated at {INDEX_FILE}")

if __name__ == "__main__":
    generate_index()
