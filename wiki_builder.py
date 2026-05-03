#!/usr/bin/env python3
"""
Wiki Builder (SkillsBuilder Pro)
Implements Karpathy's LLM Wiki pattern to transform raw emails into a structured knowledge base.
"""

import os
import json
import glob
from email_analyzer import EmailAnalyzer

import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
RAW_DIR = 'raw/emails'
WIKI_DIR = 'wiki'
ENTITY_DIR = os.path.join(WIKI_DIR, 'entities')
CONCEPT_DIR = os.path.join(WIKI_DIR, 'concepts')
INDEX_FILE = os.path.join(WIKI_DIR, 'index.md')
LOG_FILE = os.path.join(WIKI_DIR, 'log.md')

def ensure_dirs():
    os.makedirs(ENTITY_DIR, exist_ok=True)
    os.makedirs(CONCEPT_DIR, exist_ok=True)

def update_wiki_page(directory, name, type_label, description, source_email):
    """Create or update a wiki page for an entity or concept."""
    filename = f"{name.lower().replace(' ', '_')}.md"
    filepath = os.path.join(directory, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n\n### Supplemental Info (Source: {source_email})\n{description}")
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {name}\n\n")
            f.write(f"**Type**: {type_label}\n\n")
            f.write(f"## Description\n{description}\n\n")
            f.write(f"## Records\n- {source_email}")
    
    return filename

def build_wiki():
    print("Starting Wiki Builder (Karpathy Ingest Workflow)...")
    ensure_dirs()
    analyzer = EmailAnalyzer()
    
    if not analyzer.check_ollama_connection():
        print("AI service not available. Wiki building suspended.")
        return

    email_files = glob.glob(os.path.join(RAW_DIR, "*.json"))
    print(f"Found {len(email_files)} raw emails.")
    
    entities_map = {}
    concepts_map = {}
    
    for email_file in email_files:
        with open(email_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Simple skip logic: if already processed (could use a log file)
        # For now, let's process all to build the initial wiki
        
        print(f"Analyzing: {data['subject']}")
        analysis = analyzer.extract_wiki_entities(data['subject'], data['body'])
        
        source_ref = f"[{data['subject']}]({data['entry_id']})" # EntryID is unique
        
        for ent in analysis.get('entities', []):
            fname = update_wiki_page(ENTITY_DIR, ent['name'], ent['type'], ent['description'], data['subject'])
            entities_map[ent['name']] = fname
            
        for con in analysis.get('concepts', []):
            fname = update_wiki_page(CONCEPT_DIR, con['name'], "Concept", con['description'], data['subject'])
            concepts_map[con['name']] = fname

    # Update Index
    print("Updating Wiki Index...")
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write("# Project Brain: Outlook Database Tool\n\n")
        f.write("## Entities\n")
        for name, fname in sorted(entities_map.items()):
            f.write(f"- [{name}](entities/{fname})\n")
            
        f.write("\n## Concepts\n")
        for name, fname in sorted(concepts_map.items()):
            f.write(f"- [{name}](concepts/{fname})\n")
            
    # Update Log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n- {os.path.basename(LOG_FILE)}: Wiki building completed at {os.environ.get('CURRENT_TIME', '2026-05-03')}\n")

    print("Wiki Building Complete!")

if __name__ == "__main__":
    build_wiki()
