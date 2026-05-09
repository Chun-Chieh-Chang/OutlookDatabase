import os
import json
import re
import sqlite3

class EvolutionAnalyzer:
    def __init__(self, wiki_root='wiki', db_path='emails.db'):
        self.wiki_root = wiki_root
        self.db_path = db_path

    def calculate_metrics(self):
        # 1. Synthesis Rate
        dim_root = os.path.join(self.wiki_root, 'dimensions')
        total_entities = 0
        synthesized_entities = 0
        
        for r, d, fs in os.walk(dim_root):
            for f in fs:
                if f.endswith('.md'):
                    total_entities += 1
                    path = os.path.join(r, f)
                    try:
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        if "AI 深度合成報告" in content:
                            synthesized_entities += 1
                    except: pass
        
        synthesis_rate = (synthesized_entities / total_entities * 100) if total_entities > 0 else 0
        
        # 2. Link Density
        graph_path = os.path.join(self.wiki_root, 'graph_data.json')
        link_density = 0
        if os.path.exists(graph_path):
            with open(graph_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nodes = len(data.get('nodes', []))
                links = len(data.get('links', []))
                link_density = (links / nodes) if nodes > 0 else 0
        
        # 3. Data Volume
        email_count = 0
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM emails")
            email_count = cursor.fetchone()[0]
            conn.close()
        except: pass
        
        # Evolution Score (Weighted Formula)
        # Score = (Rate * 0.5) + (Density * 10) + (log10(Volume) * 2)
        import math
        volume_score = math.log10(email_count + 1) * 2
        evolution_score = (synthesis_rate * 0.4) + (link_density * 15) + volume_score
        
        # Determine Status
        status = "原地踏步 (Stagnant)"
        if evolution_score > 60: status = "快速進化 (Rapid Evolution)"
        elif evolution_score > 30: status = "持續優化 (Evolving)"
        
        return {
            "score": round(evolution_score, 1),
            "status": status,
            "synthesis_rate": round(synthesis_rate, 1),
            "link_density": round(link_density, 2),
            "total_emails": email_count,
            "total_entities": total_entities,
            "synthesized": synthesized_entities
        }

if __name__ == "__main__":
    analyzer = EvolutionAnalyzer()
    print(json.dumps(analyzer.calculate_metrics(), indent=2, ensure_ascii=False))
