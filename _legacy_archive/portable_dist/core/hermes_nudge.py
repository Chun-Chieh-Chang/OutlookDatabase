#!/usr/bin/env python3
"""
Hermes Nudge Engine (Self-Evolving Maintenance)
Part of SkillsBuilder Layer 4 (Evolution).
Scans the Library for "Low Quality" entities and nudges the Librarian to re-synthesize.
"""

import os
import re
import json
import sys
import io
from datetime import datetime

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKI_DIR = 'wiki'
ONTOLOGY_FILE = 'schema/ontology.json'

def scan_for_low_quality():
    """Find entities that need enrichment."""
    needs_nudge = []
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md') and f.lower() not in ['index.md', 'log.md']:
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    reasons = []
                    # Check 1: Empty or very short description
                    desc_match = re.search(r'## Description\n(.*?)\n##', content, re.DOTALL)
                    if desc_match:
                        desc = desc_match.group(1).strip()
                        if len(desc) < 20:
                            reasons.append("Short Description")
                    
                    # Check 2: Missing relationships
                    rel_match = re.search(r'## Relationships\n(.*?)\n##', content, re.DOTALL)
                    if rel_match:
                        rels = rel_match.group(1).strip()
                        if "- **" not in rels:
                            reasons.append("No Relationships")
                    
                    # Check 3: Missing crucial Frontmatter fields
                    if 'urgency: none' in content.lower():
                        reasons.append("Undefined Urgency")
                        
                    if reasons:
                        needs_nudge.append({
                            "file": os.path.relpath(path, WIKI_DIR),
                            "reasons": reasons
                        })
    return needs_nudge

def run_nudge():
    print("🧠 Hermes Nudge Engine: Scanning Library for Evolution Opportunities...")
    candidates = scan_for_low_quality()
    
    if not candidates:
        print("✅ Library is high quality. No nudges needed.")
        return

    print(f"⚠️ Found {len(candidates)} entities needing enrichment.")
    
    nudge_log = os.path.join(WIKI_DIR, 'nudge_list.md')
    with open(nudge_log, 'w', encoding='utf-8') as f:
        f.write(f"# Hermes Self-Evolution Nudge List\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"These entities are marked for **Re-Synthesis** due to low data density.\n\n")
        for c in candidates:
            f.write(f"- [[{c['file']}]] -> Reasons: {', '.join(c['reasons'])}\n")
            
    print(f"📝 Nudge list updated at {nudge_log}")

if __name__ == "__main__":
    run_nudge()
