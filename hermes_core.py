import os
import json
import time
import sqlite3
from datetime import datetime
from email_analyzer import EmailAnalyzer
from wiki_builder import resolve_entity_name, load_alias_registry, save_alias_registry, load_graph_store, save_graph_store, upsert_graph_node, add_graph_edge, update_wiki_page_v2, ensure_dirs

class HermesAgent:
    """
    Hermes Agent - The Knowledge Accumulator
    Automatically processes new emails and integrates them into the Knowledge Graph.
    """
    def __init__(self, state_file='hermes_state.json'):
        self.state_file = state_file
        self.analyzer = EmailAnalyzer()
        self.load_state()
        ensure_dirs()

    def load_state(self):
        if os.path.exists(self.state_file) and os.path.getsize(self.state_file) > 0:
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except:
                self.state = {"last_processed_id": 0, "total_accumulated": 0, "status": "idle"}
        else:
            self.state = {"last_processed_id": 0, "total_accumulated": 0, "status": "idle"}

    def save_state(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def accumulate(self, limit=10):
        """Scan for new emails and add to knowledge base."""
        self.state["status"] = "processing"
        self.save_state()
        
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        
        # Find emails not yet processed by Hermes
        cursor.execute("SELECT rowid, subject, body, sender_name, received_time FROM emails WHERE rowid > ? ORDER BY rowid ASC LIMIT ?", 
                       (self.state["last_processed_id"], limit))
        rows = cursor.fetchall()
        
        if not rows:
            self.state["status"] = "idle"
            self.save_state()
            return 0
        
        alias_registry = load_alias_registry()
        graph_store = load_graph_store()
        
        processed_count = 0
        for rowid, subject, body, sender, received_time in rows:
            print(f"[Hermes] Accumulating: {subject}")
            try:
                analysis = self.analyzer.extract_wiki_entities(subject, body)
                source_ref = f"[{subject}]({rowid})"
                
                if 'dimensions' in analysis:
                    for dim in analysis['dimensions']:
                        raw_name = dim['name']
                        aliases = dim.get('aliases', [])
                        cat = dim.get('category', 'event').lower()
                        
                        # Resolve Canonical Name
                        canonical_name = resolve_entity_name(raw_name, aliases, alias_registry)
                        
                        # Determine Directory
                        from wiki_builder import CAT_TO_DIR, DIM_MAP, DIMENSIONS_DIR, WIKI_DIR, LIFECYCLE_DIR, IMPROVEMENT_DIR
                        if cat in CAT_TO_DIR:
                            target_dir = CAT_TO_DIR[cat]
                        elif cat in DIM_MAP:
                            target_dir = os.path.join(DIMENSIONS_DIR, DIM_MAP[cat])
                        else:
                            target_dir = os.path.join(DIMENSIONS_DIR, 'events')
                        
                        # Update Wiki & Graph
                        wiki_filename = update_wiki_page_v2(target_dir, canonical_name, dim, source_ref)
                        
                        # PDCA/CAPA Links
                        lc = dim.get('lifecycle', 'none').lower()
                        if lc in ['plan', 'do', 'check', 'act']:
                            update_wiki_page_v2(os.path.join(LIFECYCLE_DIR, lc), canonical_name, dim, source_ref)
                        
                        imp = dim.get('improvement', 'none').lower()
                        if imp in ['problem', 'rootcause', 'correction', 'prevention']:
                            update_wiki_page_v2(os.path.join(IMPROVEMENT_DIR, imp), canonical_name, dim, source_ref)
                        
                        # Graph Node
                        rel_file = os.path.relpath(os.path.join(target_dir, wiki_filename), WIKI_DIR)
                        upsert_graph_node(graph_store, canonical_name, canonical_name, cat, aliases, [cat], dim.get('tags', []), rel_file)
                        
                        # Graph Edges
                        for rel in dim.get('relationships', []):
                            target = rel.get('target', '')
                            rtype = rel.get('type', 'related')
                            if target:
                                add_graph_edge(graph_store, canonical_name, target, rtype, str(rowid))
                
                processed_count += 1
                self.state["last_processed_id"] = rowid
                self.state["total_accumulated"] += 1
                
            except Exception as e:
                print(f"[Hermes] Error processing {rowid}: {e}")
        
        save_alias_registry(alias_registry)
        save_graph_store(graph_store)
        
        # Trigger Index Regeneration
        try:
            from wiki_index_gen import generate_index
            generate_index()
        except: pass
        
        self.state["status"] = "idle"
        self.state["last_sync"] = datetime.now().isoformat()
        self.save_state()
        
        conn.close()
        return processed_count

if __name__ == "__main__":
    agent = HermesAgent()
    count = agent.accumulate(limit=5)
    print(f"Hermes session finished. Accumulated {count} emails.")
