#!/usr/bin/env python3
"""
Wiki Builder v2 (SkillsBuilder Pro)
Implements Karpathy's LLM Wiki pattern with:
- YAML Frontmatter (Obsidian-style)
- Alias Registry (Entity Deduplication)
- Bi-directional Backlinks
- Graph Store (JSON persistence)
"""

import os
import json
import glob
import re
from datetime import datetime
from email_analyzer import EmailAnalyzer
import sys
import io

# Fix Windows encoding
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# Paths
RAW_DIR = 'raw/emails'
WIKI_DIR = 'wiki'
SCHEMA_DIR = 'schema'
ONTOLOGY_FILE = os.path.join(SCHEMA_DIR, 'ontology.json')
DIMENSIONS_DIR = os.path.join(WIKI_DIR, 'dimensions')
LIFECYCLE_DIR = os.path.join(WIKI_DIR, 'lifecycle')
IMPROVEMENT_DIR = os.path.join(WIKI_DIR, 'improvement')
PROJECTS_DIR = os.path.join(WIKI_DIR, 'projects')
ORGANIZATIONS_DIR = os.path.join(WIKI_DIR, 'organizations')
ARTIFACTS_DIR = os.path.join(WIKI_DIR, 'artifacts')
DOMAINS_DIR = os.path.join(WIKI_DIR, 'domains')
ENTITY_DIR = os.path.join(WIKI_DIR, 'entities') 
CONCEPT_DIR = os.path.join(WIKI_DIR, 'concepts') 
INDEX_FILE = os.path.join(WIKI_DIR, 'index.md')
LOG_FILE = os.path.join(WIKI_DIR, 'log.md')
ALIAS_REGISTRY_FILE = os.path.join(WIKI_DIR, '.alias_registry.json')
GRAPH_STORE_FILE = os.path.join(WIKI_DIR, 'graph_store.json')

# Load Ontology Schema
def load_ontology():
    if os.path.exists(ONTOLOGY_FILE):
        with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

ONTOLOGY = load_ontology()

# Multi-dimensional Semantic Clustering (HR, PQC, QMS, Contextual Domains...) - Dynamic fallback
DIM_MAP = {
    'man': 'man',
    'machine': 'machine',
    'material': 'material',
    'method': 'method',
    'env': 'environment',
    'measure': 'measurement',
    'hr': 'hr',
    'admin': 'admin',
    'event': 'events',
    'others': 'others'
}

# Category to Root Directory mapping
CAT_TO_DIR = {
    'project': PROJECTS_DIR,
    'org': ORGANIZATIONS_DIR,
    'artifact': ARTIFACTS_DIR,
    'domain': DOMAINS_DIR,
    'quality': IMPROVEMENT_DIR,
    'lifecycle': LIFECYCLE_DIR
}

# ═══════════════════════════════════════════
# Alias Registry (Entity Deduplication)
# ═══════════════════════════════════════════

def load_alias_registry():
    """Load alias → canonical_name mapping."""
    if os.path.exists(ALIAS_REGISTRY_FILE):
        with open(ALIAS_REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_alias_registry(registry):
    """Persist alias registry."""
    with open(ALIAS_REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def resolve_entity_name(name, aliases, registry):
    """Resolve entity name via alias registry. Returns canonical name.
    
    Logic:
    1. If `name` is already a known alias → return its canonical name
    2. If any alias is already a known alias → return its canonical name
    3. Otherwise → register `name` as canonical and all aliases as pointing to it
    """
    name_key = name.lower().strip()
    
    # Check if this name is a known alias
    if name_key in registry:
        return registry[name_key]
    
    # Check if any alias is already registered
    for alias in aliases:
        alias_key = alias.lower().strip()
        if alias_key in registry:
            # Found existing canonical → register current name as alias too
            canonical = registry[alias_key]
            registry[name_key] = canonical
            return canonical
    
    # New entity → register canonical + all aliases
    canonical = name.strip()
    registry[name_key] = canonical
    for alias in aliases:
        alias_key = alias.lower().strip()
        if alias_key:
            registry[alias_key] = canonical
    
    return canonical

# ═══════════════════════════════════════════
# Graph Store (Edge Persistence)
# ═══════════════════════════════════════════

def load_graph_store():
    """Load or initialize graph store."""
    if os.path.exists(GRAPH_STORE_FILE):
        with open(GRAPH_STORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "meta": {"version": "2.0", "updated": "", "node_count": 0, "edge_count": 0},
        "nodes": {},
        "edges": []
    }

def save_graph_store(store):
    """Persist graph store."""
    store["meta"]["updated"] = datetime.now().isoformat()
    store["meta"]["node_count"] = len(store["nodes"])
    store["meta"]["edge_count"] = len(store["edges"])
    with open(GRAPH_STORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(store, f, indent=2, ensure_ascii=False)

def upsert_graph_node(store, entity_id, label, entity_type, aliases, dimensions, tags, file_path):
    """Add or update a node in the graph store."""
    node_key = entity_id.lower().replace(' ', '_')
    if node_key in store["nodes"]:
        # Merge new info
        existing = store["nodes"][node_key]
        existing["aliases"] = list(set(existing.get("aliases", []) + aliases))
        existing["tags"] = list(set(existing.get("tags", []) + tags))
        existing["dimensions"] = list(set(existing.get("dimensions", []) + dimensions))
    else:
        store["nodes"][node_key] = {
            "id": node_key,
            "label": label,
            "type": entity_type,
            "aliases": aliases,
            "dimensions": dimensions,
            "tags": tags,
            "file": file_path
        }

def add_graph_edge(store, source, target, relation, source_email=""):
    """Add an edge (skip duplicates)."""
    src_key = source.lower().replace(' ', '_')
    tgt_key = target.lower().replace(' ', '_')
    
    # Deduplicate
    for edge in store["edges"]:
        if edge["source"] == src_key and edge["target"] == tgt_key and edge["relation"] == relation:
            return
    
    store["edges"].append({
        "source": src_key,
        "target": tgt_key,
        "relation": relation,
        "source_email": source_email
    })

# ═══════════════════════════════════════════
# YAML Frontmatter Wiki Page Writer
# ═══════════════════════════════════════════

def sanitize_filename(name):
    """Create a safe filename from entity name."""
    safe = name.lower().replace(' ', '_')
    safe = re.sub(r'[<>:"/\\|?*]', '', safe)
    safe = safe.strip('._')
    if not safe:
        safe = 'unnamed'
    return f"{safe}.md"

def update_wiki_page_v2(directory, canonical_name, dim_data, source_email, analyzer=None):
    """Create or update a wiki page with YAML frontmatter (Obsidian-style).
    
    Args:
        directory: Target directory for the page
        canonical_name: Resolved canonical entity name
        dim_data: Full dimension dict from LLM (with aliases, tags, etc.)
        source_email: Source reference string
        analyzer: Optional EmailAnalyzer for synthesis
    """
    filename = sanitize_filename(canonical_name)
    filepath = os.path.join(directory, filename)
    
    category = dim_data.get('category', 'event')
    description = dim_data.get('description', '').strip()
    aliases = dim_data.get('aliases', [])
    tags = dim_data.get('tags', [])
    lifecycle = dim_data.get('lifecycle', 'do')
    improvement = dim_data.get('improvement', 'none')
    urgency = dim_data.get('urgency', 'normal')
    domain = dim_data.get('domain', '')
    relationships = dim_data.get('relationships', [])
    
    if os.path.exists(filepath):
        if analyzer:
            # Synthesis Mode: AI merges new info into existing content
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            new_evidence = f"Category: {category}\nDescription: {description}\n"
            if relationships:
                new_evidence += "Relationships: " + ", ".join([f"[[{r['target']}]] ({r['type']})" for r in relationships if r.get('target')])
            
            synthesized = analyzer.synthesize_wiki_page(existing_content, new_evidence, source_email)
            
            if synthesized and "---" in synthesized:
                # Clean up markdown code blocks if any
                synthesized = synthesized.strip()
                if synthesized.startswith('```'):
                    synthesized = re.sub(r'^```(?:markdown)?\s*', '', synthesized)
                    synthesized = re.sub(r'\s*```$', '', synthesized)
                
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(synthesized)
                return filename

        # Fallback to Append mode if no analyzer or synthesis failed
        with open(filepath, 'a', encoding='utf-8-sig') as f:
            f.write(f"\n\n### Record (Source: {source_email})\n")
            if description:
                f.write(f"{description}\n")
            # Append relationship links
            if relationships:
                f.write("\n**Links**: ")
                links = [f"[[{r['target']}]] ({r['type']})" for r in relationships if r.get('target')]
                f.write(" · ".join(links))
                f.write("\n")
    else:
        # Create mode: write full page with YAML frontmatter
        now = datetime.now().strftime('%Y-%m-%d')
        
        with open(filepath, 'w', encoding='utf-8-sig') as f:

            # YAML Frontmatter
            f.write("---\n")
            f.write(f"title: \"{canonical_name}\"\n")
            if aliases:
                f.write(f"aliases: {json.dumps(aliases, ensure_ascii=False)}\n")
            f.write(f"type: {category}\n")
            f.write(f"dimensions: [{category}]\n")
            f.write(f"lifecycle: {lifecycle}\n")
            f.write(f"improvement: {improvement}\n")
            f.write(f"urgency: {urgency}\n")
            if tags:
                f.write(f"tags: {json.dumps(tags, ensure_ascii=False)}\n")
            if domain:
                f.write(f"domain: \"{domain}\"\n")
            f.write(f"created: {now}\n")
            f.write(f"updated: {now}\n")
            f.write("---\n\n")
            
            # Markdown Body
            f.write(f"# {canonical_name}\n\n")
            
            # Description
            f.write(f"## Description\n")
            f.write(f"{description}\n\n")
            
            # Relationships as wiki-links
            if relationships:
                f.write("## Relationships\n")
                for rel in relationships:
                    target = rel.get('target', '')
                    rtype = rel.get('type', 'related')
                    if target:
                        f.write(f"- **{rtype}**: [[{target}]]\n")
                f.write("\n")
            
            # Records
            f.write(f"## Records\n")
            f.write(f"- {source_email}\n")
    
    return filename

# ═══════════════════════════════════════════
# Directory Setup
# ═══════════════════════════════════════════

def ensure_dirs():
    os.makedirs(WIKI_DIR, exist_ok=True)
    os.makedirs(DIMENSIONS_DIR, exist_ok=True)
    for sub in DIM_MAP.values():
        os.makedirs(os.path.join(DIMENSIONS_DIR, sub), exist_ok=True)
    
    # PDCA Lifecycle views
    os.makedirs(LIFECYCLE_DIR, exist_ok=True)
    for sub in ['plan', 'do', 'check', 'act']:
        os.makedirs(os.path.join(LIFECYCLE_DIR, sub), exist_ok=True)
    
    # CAPA Improvement views
    os.makedirs(IMPROVEMENT_DIR, exist_ok=True)
    for sub in ['problem', 'rootcause', 'correction', 'prevention']:
        os.makedirs(os.path.join(IMPROVEMENT_DIR, sub), exist_ok=True)
        
    # Industrial Core Views
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(ORGANIZATIONS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    os.makedirs(DOMAINS_DIR, exist_ok=True)
    
    # Maintain legacy for compatibility
    os.makedirs(ENTITY_DIR, exist_ok=True)
    os.makedirs(CONCEPT_DIR, exist_ok=True)

# ═══════════════════════════════════════════
# Processed Email Tracking
# ═══════════════════════════════════════════

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

# ═══════════════════════════════════════════
# Main Build Pipeline
# ═══════════════════════════════════════════

def build_wiki():
    print("Starting Wiki Builder v2 (Frontmatter + Alias + Graph)...")
    ensure_dirs()
    analyzer = EmailAnalyzer()
    
    if not analyzer.check_ollama_connection():
        print("AI service not available. Wiki building suspended.")
        return
    
    # Load persistent state
    processed_emails = get_processed_emails()
    alias_registry = load_alias_registry()
    graph_store = load_graph_store()
    
    print(f"Previously processed: {len(processed_emails)} emails")
    print(f"Alias Registry: {len(alias_registry)} entries")
    print(f"Graph Store: {graph_store['meta'].get('node_count', 0)} nodes, {graph_store['meta'].get('edge_count', 0)} edges")
    
    # Filter new emails only
    new_emails = []
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    print(f"🔍 正在掃描本地原始數據目錄: {RAW_DIR} ...", flush=True)
    
    # Use os.scandir for high performance
    all_emails = []
    with os.scandir(RAW_DIR) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith('.json'):
                all_emails.append(entry.path)
    
    print(f"📊 發現共 {len(all_emails)} 封原始郵件，篩選前 {limit} 封...", flush=True)
    
    for email_file in all_emails:
        if len(new_emails) >= limit:
            break
            
        eid = os.path.basename(email_file).replace('.json', '')
        if eid not in processed_emails:
            try:
                if os.path.getsize(email_file) == 0:
                    continue
                with open(email_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                new_emails.append((email_file, data))
                
                processed_count += 1
                elapsed = time.time() - start_time
                percentage = min(100, int((processed_count / total_emails) * 100))
                
                # 寫入結構化進度檔案供 UI 讀取
                progress_data = {
                    "percentage": percentage,
                    "processed": processed_count,
                    "total": total_emails,
                    "elapsed_seconds": int(elapsed),
                    "status": "Loading..."
                }
                with open('logs/progress.json', 'w', encoding='utf-8') as pf:
                    json.dump(progress_data, pf)

                if len(new_emails) % 10 == 0:
                    print(f"  -> 已加載 {len(new_emails)} 封郵件... ({percentage}% | 耗時: {int(elapsed)}s)", flush=True)
            except Exception as e:
                continue

    if not new_emails:
        print("✅ 確效完成：所有本地資料已結構化，無需重複建構。", flush=True)
        return
        
    print(f"🚀 偵測到 {len(new_emails)} 封新郵件待提取，開始知識映射程序...", flush=True)
    
    session_stats = {"processed": 0, "entities": 0, "edges": 0, "errors": 0}
    
    for email_file, data in new_emails:
        print(f"  > 正在分析: {data['subject']} ...", flush=True)
        try:
            analysis = analyzer.extract_wiki_entities(data['subject'], data['body'])
            
            source_ref = f"[{data['subject']}]({data['entry_id']})"
            
            # Process Multi-dimensional Knowledge (v2)
            if 'dimensions' in analysis:
                for dim in analysis['dimensions']:
                    raw_name = dim['name']
                    aliases = dim.get('aliases', [])
                    cat = dim.get('category', 'event').lower()
                    desc = dim.get('description', '')
                    
                    # ═══ Step 1: Resolve Entity Name via Alias Registry ═══
                    canonical_name = resolve_entity_name(raw_name, aliases, alias_registry)
                    
                    # ═══ Step 2: Route to Primary Directory ═══
                    if cat in CAT_TO_DIR:
                        target_dir = CAT_TO_DIR[cat]
                    elif cat in DIM_MAP:
                        target_sub = DIM_MAP[cat]
                        target_dir = os.path.join(DIMENSIONS_DIR, target_sub)
                    else:
                        target_dir = os.path.join(DIMENSIONS_DIR, 'events')
                    
                    # ═══ Step 3: Write Wiki Page (v2 with frontmatter) ═══
                    wiki_filename = update_wiki_page_v2(target_dir, canonical_name, dim, source_ref, analyzer=analyzer)
                    
                    # ═══ Step 4: Cross-link to Lifecycle View (PDCA) ═══
                    lc = dim.get('lifecycle', 'none').lower()
                    if lc in ['plan', 'do', 'check', 'act']:
                        update_wiki_page_v2(os.path.join(LIFECYCLE_DIR, lc), canonical_name, dim, source_ref, analyzer=analyzer)
                        
                    # ═══ Step 5: Cross-link to Improvement View (CAPA) ═══
                    imp = dim.get('improvement', 'none').lower()
                    if imp in ['problem', 'rootcause', 'correction', 'prevention']:
                        update_wiki_page_v2(os.path.join(IMPROVEMENT_DIR, imp), canonical_name, dim, source_ref, analyzer=analyzer)
                    
                    # ═══ Step 6: Update Graph Store ═══
                    rel_file = os.path.relpath(os.path.join(target_dir, wiki_filename), WIKI_DIR)
                    upsert_graph_node(
                        graph_store, canonical_name, canonical_name, cat,
                        aliases, [cat], dim.get('tags', []), rel_file
                    )
                    
                    for rel in dim.get('relationships', []):
                        target = rel.get('target', '')
                        rtype = rel.get('type', 'related')
                        if target:
                            add_graph_edge(graph_store, canonical_name, target, rtype, data['entry_id'])
                            session_stats["edges"] += 1
                    
                    session_stats["entities"] += 1
            
            mark_email_processed(data['entry_id'])
            session_stats["processed"] += 1
            
        except Exception as e:
            print(f"Error analyzing {data['subject']}: {e}")
            session_stats["errors"] += 1
            continue
    
    # Persist state
    save_alias_registry(alias_registry)
    save_graph_store(graph_store)
    
    print(f"\n{'='*50}", flush=True)
    print(f"Session Complete:", flush=True)
    print(f"  Emails Processed: {session_stats['processed']}", flush=True)
    print(f"  Entities Created/Updated: {session_stats['entities']}", flush=True)
    print(f"  Edges Added: {session_stats['edges']}", flush=True)
    print(f"  Errors: {session_stats['errors']}", flush=True)
    print(f"  Alias Registry Size: {len(alias_registry)}", flush=True)
    print(f"  Graph Nodes: {graph_store['meta']['node_count']}", flush=True)
    print(f"  Graph Edges: {graph_store['meta']['edge_count']}", flush=True)
    print(f"{'='*50}", flush=True)

if __name__ == "__main__":
    build_wiki()
