import os
import shutil
import re

WIKI_DIR = 'wiki'
ENTITY_DIR = os.path.join(WIKI_DIR, 'entities')
CONCEPT_DIR = os.path.join(WIKI_DIR, 'concepts')
DIMENSIONS_DIR = os.path.join(WIKI_DIR, 'dimensions')

# Define target subdirectories
SUB_DIRS = {
    'man': ['man', 'people', 'contacts'],
    'machine': ['machine', 'equipment', 'tools', 'instruments'],
    'material': ['material', 'parts', 'chemicals', 'products'],
    'method': ['method', 'sop', 'process', 'logic', 'regulation'],
    'environment': ['environment', 'location', 'site', 'market'],
    'measurement': ['measurement', 'quality', 'data', 'calibration'],
    'events': ['events', 'timeline', 'milestones']
}

import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def migrate():
    print("🚀 Starting Wiki Migration to Industrial Dimensions (人機料法環測)...")
    
    # Create target directories
    for sub in SUB_DIRS.keys():
        os.makedirs(os.path.join(DIMENSIONS_DIR, sub), exist_ok=True)
    os.makedirs(os.path.join(DIMENSIONS_DIR, 'others'), exist_ok=True)

    # Process entities and concepts
    source_dirs = [ENTITY_DIR, CONCEPT_DIR]
    
    for source_dir in source_dirs:
        if not os.path.exists(source_dir): continue
        
        files = [f for f in os.listdir(source_dir) if f.endswith('.md')]
        for filename in files:
            filepath = os.path.join(source_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # Heuristic Classification
            target_sub = 'others'
            
            # Man: People, Email, Phone, Company
            if any(x in content for x in ['person', 'contact', 'people', 'email', 'phone', '公司', '經理', '小姐', '先生']):
                target_sub = 'man'
            # Machine: Tool, Equipment, Instrument
            elif any(x in content for x in ['tool', 'machine', 'equipment', 'instrument', '顯微鏡', '量測儀', '儀器']):
                target_sub = 'machine'
            # Material: Parts, P/N, Material
            elif any(x in content for x in ['part', 'material', 'p/n', '零件', '產品', '原料', '鍍層']):
                target_sub = 'material'
            # Method: SOP, PQ, Process, Rule
            elif any(x in content for x in ['sop', 'process', 'regulation', '決策', '流程', '計畫', '規範', 'iq', 'oq', 'pq']):
                target_sub = 'method'
            # Measurement: Data, Quality, Calibration
            elif any(x in content for x in ['quality', 'data', 'calibration', '品質', '數據', '校正', '測量']):
                target_sub = 'measurement'
            # Environment: Site, Location
            elif any(x in content for x in ['location', 'site', 'factory', '場域', '位置', '廠']):
                target_sub = 'environment'
            
            # Perform Move
            dest_path = os.path.join(DIMENSIONS_DIR, target_sub, filename)
            shutil.move(filepath, dest_path)
            print(f"Moved {filename} -> dimensions/{target_sub}/")

    print("✅ Migration Complete.")

if __name__ == "__main__":
    migrate()
