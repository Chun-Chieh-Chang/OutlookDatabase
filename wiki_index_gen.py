import os

WIKI_DIR = 'wiki'
DIMENSIONS_DIR = os.path.join(WIKI_DIR, 'dimensions')
INDEX_FILE = os.path.join(WIKI_DIR, 'index.md')

DIM_LABELS = {
    'man': '👤 人 (Man/Who) - 權責與通訊網絡',
    'machine': '⚙️ 機 (Machine) - 設備與工具',
    'material': '📦 料 (Material) - 物料與產品實體',
    'method': '📜 法 (Method) - 工藝、SOP 與決策流程',
    'environment': '🌍 環 (Environment) - 場域與外部環境',
    'measurement': '📏 測 (Measurement) - 品質與量測數據',
    'events': '📅 時與事 (Events) - 專案里程碑與異常事件',
    'others': '📁 其他 (Others)'
}

PDCA_LABELS = {
    'plan': '🔵 Plan (計畫與目標)',
    'do': '🟢 Do (執行紀錄)',
    'check': '🟡 Check (檢查與驗證)',
    'act': '🔴 Act (優化與標準化)'
}

CAPA_LABELS = {
    'problem': '⚠️ Problem (異常發現)',
    'rootcause': '🔍 Root Cause (原因分析)',
    'correction': '🔧 Correction (立即對策)',
    'prevention': '🛡️ Prevention (預防措施)'
}

CORE_LABELS = {
    'projects': '🏗️ 專案維度 (Projects) - 產品與專案體系',
    'organizations': '🏢 組織維度 (Organizations) - 公司與利害關係人',
    'artifacts': '📄 文件與產出 (Artifacts) - 圖面、報告與證物',
    'domains': '🧪 技術領域 (Domains) - 專業領域知識'
}

def generate_index():
    print("📋 Generating Categorized Wiki Index...")
    
    # Load graph stats if available
    graph_stats = {"node_count": 0, "edge_count": 0, "updated": "N/A"}
    alias_count = 0
    graph_store_path = os.path.join(WIKI_DIR, 'graph_store.json')
    alias_registry_path = os.path.join(WIKI_DIR, '.alias_registry.json')
    
    if os.path.exists(graph_store_path):
        try:
            import json
            with open(graph_store_path, 'r', encoding='utf-8') as gf:
                gs = json.load(gf)
                graph_stats = gs.get("meta", graph_stats)
        except: pass
    
    if os.path.exists(alias_registry_path):
        try:
            import json
            with open(alias_registry_path, 'r', encoding='utf-8') as af:
                alias_count = len(json.load(af))
        except: pass
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write("# SkillsBuilder 工業知識圖譜 v2 (Industrial Knowledge Graph)\n\n")
        f.write("> 本索引整合「核心維度」、「資源管理(4M1E)」、「生命週期(PDCA)」與「改善機制(CAPA)」，提供全方位決策支援。\n\n")
        
        # Graph Stats Summary
        f.write("## 📊 圖譜統計 (Graph Stats)\n")
        f.write(f"| Metric | Value |\n|--------|-------|\n")
        f.write(f"| Nodes | {graph_stats.get('node_count', 0)} |\n")
        f.write(f"| Edges | {graph_stats.get('edge_count', 0)} |\n")
        f.write(f"| Aliases | {alias_count} |\n")
        f.write(f"| Updated | {graph_stats.get('updated', 'N/A')[:19]} |\n\n")
        
        f.write("## 🏛️ 核心治理維度 (Core Views)\n")
        for dim, label in CORE_LABELS.items():
            dim_path = os.path.join(WIKI_DIR, dim)
            if not os.path.exists(dim_path): continue
            files = sorted([file for file in os.listdir(dim_path) if file.endswith('.md')])
            if not files: continue
            f.write(f"### {label}\n")
            for filename in files:
                name = filename.replace('.md', '')
                f.write(f"* [{name}]({dim}/{filename})\n")
            f.write("\n")

        f.write("## 🛠️ 資源維度 (4M1E View)\n")
        for dim, label in DIM_LABELS.items():
            dim_path = os.path.join(DIMENSIONS_DIR, dim)
            if not os.path.exists(dim_path): continue
            files = sorted([file for file in os.listdir(dim_path) if file.endswith('.md')])
            if not files: continue
            f.write(f"### {label}\n")
            for filename in files:
                name = filename.replace('.md', '')
                f.write(f"* [{name}](dimensions/{dim}/{filename})\n")
            f.write("\n")

        f.write("## 🔄 管理週期維度 (PDCA View)\n")
        for dim, label in PDCA_LABELS.items():
            dim_path = os.path.join(WIKI_DIR, 'lifecycle', dim)
            if not os.path.exists(dim_path): continue
            files = sorted([file for file in os.listdir(dim_path) if file.endswith('.md')])
            if not files: continue
            f.write(f"### {label}\n")
            for filename in files:
                name = filename.replace('.md', '')
                f.write(f"* [{name}](lifecycle/{dim}/{filename})\n")
            f.write("\n")

        f.write("## 📈 改善與品質維度 (CAPA View)\n")
        for dim, label in CAPA_LABELS.items():
            dim_path = os.path.join(WIKI_DIR, 'improvement', dim)
            if not os.path.exists(dim_path): continue
            files = sorted([file for file in os.listdir(dim_path) if file.endswith('.md')])
            if not files: continue
            f.write(f"### {label}\n")
            for filename in files:
                name = filename.replace('.md', '')
                f.write(f"* [{name}](improvement/{dim}/{filename})\n")
            f.write("\n")
            
    print(f"✅ Index generated at {INDEX_FILE}")

if __name__ == "__main__":
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    generate_index()
