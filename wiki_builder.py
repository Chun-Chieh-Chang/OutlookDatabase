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

def get_processed_emails():
    """Get set of already processed email entry IDs."""
    processed_file = os.path.join(WIKI_DIR, '.processed_emails.txt')
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def mark_email_processed(entry_id):
    """Mark an email as processed."""
    processed_file = os.path.join(WIKI_DIR, '.processed_emails.txt')
    with open(processed_file, 'a', encoding='utf-8') as f:
        f.write(f"{entry_id}\n")

def build_wiki():
    print("Starting Wiki Builder (Karpathy Ingest Workflow)...")
    ensure_dirs()
    analyzer = EmailAnalyzer()
    
    if not analyzer.check_ollama_connection():
        print("AI service not available. Wiki building suspended.")
        return
    
    email_files = glob.glob(os.path.join(RAW_DIR, "*.json"))
    print(f"Found {len(email_files)} raw emails.")
    
    # Get already processed emails
    processed_emails = get_processed_emails()
    print(f"Previously processed: {len(processed_emails)} emails")
    
    # Filter new emails only
    new_emails = []
    # Add a safety limit (can be passed via argv)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    for email_file in email_files:
        if len(new_emails) >= limit:
            break
            
        with open(email_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data['entry_id'] not in processed_emails:
            new_emails.append((email_file, data))
    
    print(f"Targeting {len(new_emails)} emails for this session (Limit: {limit}).")
    
    if not new_emails:
        print("No new emails found. Wiki is up to date.")
        return
    
    for email_file, data in new_emails:
        print(f"Analyzing: {data['subject']}")
        try:
            analysis = analyzer.extract_wiki_entities(data['subject'], data['body'])
            
            source_ref = f"[{data['subject']}]({data['entry_id']})"
            
            # Process entities
            for ent in analysis.get('entities', []):
                update_wiki_page(ENTITY_DIR, ent['name'], ent['type'], ent['description'], source_ref)
            
            # Process concepts
            for conc in analysis.get('concepts', []):
                update_wiki_page(CONCEPT_DIR, conc['name'], 'Concept', conc['description'], source_ref)
            
            mark_email_processed(data['entry_id'])
        except Exception as e:
            print(f"Error analyzing {data['subject']}: {e}")
            continue
            
    print("Batch processing complete.")

if __name__ == "__main__":
    build_wiki()
