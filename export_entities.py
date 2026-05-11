import os
import json
import csv
from datetime import datetime

WIKI_DIR = 'wiki/dimensions'
OUTPUT_FILE = 'Entity_Registry_2026.csv'

def export_registry():
    print(f"Scanning {WIKI_DIR} for entities...")
    data = []
    
    # Check if we have graph data to add connectivity weight
    graph_weights = {}
    graph_path = 'wiki/graph_data.json'
    if os.path.exists(graph_path):
        try:
            with open(graph_path, 'r', encoding='utf-8') as f:
                graph = json.load(f)
                for node in graph.get('nodes', []):
                    graph_weights[node['id']] = node.get('val', 0)
        except: pass

    for root, dirs, files in os.walk(WIKI_DIR):
        category = os.path.basename(root).upper()
        if category == 'DIMENSIONS': continue # Skip root
        
        for f in files:
            if f.endswith('.md'):
                name = f.replace('.md', '')
                weight = graph_weights.get(name, 0)
                data.append({
                    'Name': name,
                    'Category': category,
                    'Weight (Connectivity)': weight,
                    'Updated Date': datetime.now().strftime('%Y-%m-%d'),
                    'File Path': os.path.join(root, f)
                })

    if not data:
        print("❌ No entities found to export.")
        return

    # Sort by Weight descending
    data.sort(key=lambda x: x['Weight (Connectivity)'], reverse=True)

    keys = data[0].keys()
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    
    print(f"Exported {len(data)} entities to {OUTPUT_FILE}")

if __name__ == "__main__":
    export_registry()
