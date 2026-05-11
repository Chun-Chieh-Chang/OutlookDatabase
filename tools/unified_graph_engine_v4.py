#!/usr/bin/env python3
"""
Unified Graph Engine v4 (Hyper-Speed Edition)
Uses Word-Set Intersection for O(1) matching. 
Full 27k email scan in seconds. High-fidelity results.
"""

import os
import re
import json
import sqlite3
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKI_DIR = 'wiki/dimensions'
OUTPUT_FILE = 'wiki/graph_data.json'
DB_PATH = 'emails.db'

def get_dimension_color(path):
    path_lower = path.lower()
    if 'pqc' in path_lower: return "#10B981" # Emerald (PQC)
    if 'hr' in path_lower: return "#3B82F6"  # Royal Blue (HR)
    if 'spec' in path_lower: return "#F59E0B" # Amber (Spec)
    if 'qms' in path_lower: return "#8B5CF6" # Violet (QMS)
    if 'admin' in path_lower: return "#64748B" # Slate (Admin)
    if 'recruitment' in path_lower: return "#C084FC" # Light Purple (Recruitment)
    return "#94A3B8"

def get_synthesized_entities():
    entities = {}
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md'):
                name = f.replace('.md', '')
                entities[name] = {
                    "id": name, 
                    "color": get_dimension_color(root), 
                    "val": 10
                }
    return entities

def run_hyperspeed_engine():
    print("🚀 Starting Hyper-Speed Graph Engine v4 [VISUAL OVERHAUL]...")
    wiki_entities = get_synthesized_entities()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT body FROM emails WHERE body IS NOT NULL")
    
    links_count = {}
    word_to_eid = {}
    for name in wiki_entities.keys():
        parts = re.findall(r'\w+', name.lower())
        for p in parts:
            if len(p) > 2:
                if p not in word_to_eid: word_to_eid[p] = []
                word_to_eid[p].append(name)

    processed = 0
    for row in c:
        body_words = set(re.findall(r'\w+', row[0].lower()))
        found_in_body = set()
        intersect = body_words.intersection(word_to_eid.keys())
        for word in intersect:
            for eid in word_to_eid[word]:
                found_in_body.add(eid)
        
        if len(found_in_body) > 1:
            sorted_entities = sorted(list(found_in_body))
            for i in range(len(sorted_entities)):
                for j in range(i+1, len(sorted_entities)):
                    pair = (sorted_entities[i], sorted_entities[j])
                    links_count[pair] = links_count.get(pair, 0) + 1
        
        processed += 1
    conn.close()

    # TIERED THRESHOLDS: Logic by category
    # High Value (Technical/Process) -> Sensitive
    # Medium Value (People/Admin) -> Hardened
    def get_threshold(eid):
        # We need to know the category of the entity to set the threshold
        # wiki_entities stores this info indirectly via color or we can look up root
        color = wiki_entities.get(eid, {}).get('color', '')
        if color in ["#10B981", "#F59E0B", "#8B5CF6"]: # PQC, Spec, QMS (High Value)
            return 100 
        return 400 # HR, Admin, Recruitment (Medium Value - Hardened)

    node_weights = {eid: 0 for eid in wiki_entities.keys()}
    links = []
    
    for (s, t), weight in links_count.items():
        threshold_s = get_threshold(s)
        threshold_t = get_threshold(t)
        # Only link if weight passes the higher of the two thresholds to prevent noise
        if weight > max(threshold_s, threshold_t):
            links.append({"source": s, "target": t, "weight": weight})
            node_weights[s] += 1
            node_weights[t] += 1

    nodes = []
    for eid, info in wiki_entities.items():
        # Visual Hierarchy: Spec/PQC/QMS nodes start bigger
        base_val = 15 if info['color'] in ["#10B981", "#F59E0B", "#8B5CF6"] else 5
        final_val = base_val + min(node_weights.get(eid, 0) * 1.5, 30)
        
        nodes.append({
            "id": eid, 
            "name": eid, 
            "val": final_val, 
            "color": info['color'],
            "group": info['color']
        })

    graph = {"nodes": nodes, "links": links}
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    
    print(f"✅ VISUAL OVERHAUL COMPLETE: {len(nodes)} nodes, {len(links)} links.")

if __name__ == "__main__":
    run_hyperspeed_engine()
