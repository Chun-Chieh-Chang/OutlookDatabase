import os
import json
import re
import sqlite3
import pandas as pd
from datetime import datetime
import sys

# Try to import extended format libraries
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# Fix pathing to import EmailAnalyzer
sys.path.append(os.getcwd())
from email_analyzer import EmailAnalyzer

class KnowledgeGateway:
    """
    Unified Knowledge Gateway v1.0
    Supports: PDF, DOCX, XLSX, HTML, TXT, MD
    Goal: Transform unstructured company standards into Structured Wiki Nodes.
    """
    def __init__(self, raw_dir='raw/standards', wiki_root='wiki/dimensions'):
        self.raw_dir = raw_dir
        self.wiki_root = wiki_root
        self.analyzer = EmailAnalyzer()
        self.stats = {"processed": 0, "failed": 0, "skipped": 0}

    def log(self, msg):
        print(f"[KnowledgeGateway] {msg}")

    def extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        content = ""
        
        try:
            if ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            elif ext == '.pdf':
                if HAS_PDF:
                    with pdfplumber.open(file_path) as pdf:
                        content = "\n".join([page.extract_text() or "" for page in pdf.pages])
                else:
                    self.log(f"⚠️ Missing 'pdfplumber'. Skip PDF: {file_path}")
            
            elif ext == '.docx':
                if HAS_DOCX:
                    doc = docx.Document(file_path)
                    content = "\n".join([para.text for para in doc.paragraphs])
                else:
                    self.log(f"⚠️ Missing 'python-docx'. Skip Word: {file_path}")
            
            elif ext in ['.xlsx', '.xls']:
                # For Excel, we convert sheets to Markdown tables
                df_dict = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, df in df_dict.items():
                    content += f"\n### Sheet: {sheet_name}\n"
                    content += df.to_markdown(index=False)
            
            elif ext in ['.html', '.htm']:
                if HAS_BS4:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        soup = BeautifulSoup(f, 'html.parser')
                        # Remove scripts and styles
                        for script in soup(["script", "style"]):
                            script.decompose()
                        content = soup.get_text(separator='\n')
                else:
                    self.log(f"⚠️ Missing 'beautifulsoup4'. Skip HTML: {file_path}")
                    
        except Exception as e:
            self.log(f"❌ Error extracting {file_path}: {e}")
            return None
            
        return content.strip()

    def process_folder(self):
        if not os.path.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
            self.log(f"Created {self.raw_dir}. Please drop your ISO/SOP files there.")
            return

        all_files = []
        for root, dirs, files in os.walk(self.raw_dir):
            for f in files:
                all_files.append(os.path.join(root, f))
        
        self.log(f"🚀 Starting ingestion of {len(all_files)} files (recursive scan)...")

        for file_path in all_files:
            filename = os.path.basename(file_path)
            self.log(f"--- Processing: {filename} ---")
            
            text = self.extract_text(file_path)
            if not text or len(text) < 10:
                self.log(f"⏭️  Skipping empty or unsupported file: {filename}")
                self.stats["skipped"] += 1
                continue

            # AI Synthesis: Identify category and generate structured node
            try:
                # We use a specialized prompt for Standards Ingestion
                prompt = f"Analyze this company document and extract its technical core.\nFile: {filename}\nContent Sample: {text[:2000]}"
                system_prompt = """
                You are a Quality System Auditor (ISO 9001/13485). 
                Extract the knowledge into a Wiki dimension.
                Categories: [qms, spec, process, audit, client, vendor]
                Respond with JSON: {"name": "Canonical Title", "category": "qms/spec/...", "description": "High-level summary", "tags": ["#sop", "#iso",...]}
                """
                
                res = self.analyzer.extract_entities(subject=f"Standard: {filename}", body=text[:3000])
                
                # If AI returned dimensions, use the first one as primary
                if res.get('dimensions'):
                    ent = res['dimensions'][0]
                    # Override description with a deeper summary if needed
                    ent['description'] = f"(Source: {filename})\n" + ent.get('description', '') + f"\n\n## Full Content Reference\n{text[:5000]}"
                    if len(text) > 5000:
                        ent['description'] += "\n\n*(Note: Content truncated for Wiki storage. See original file for full details)*"
                    
                    # Force a "standard" tag
                    if 'tags' not in ent: ent['tags'] = []
                    ent['tags'].append("#source_of_truth")
                    
                    # Save as Wiki Node
                    success = self.analyzer.save_wiki_entity(ent, frequency="ORIGINAL_DOC")
                    if success:
                        self.log(f"✅ Integrated as Wiki Node: {ent['name']}")
                        self.stats["processed"] += 1
                    else:
                        self.stats["failed"] += 1
                else:
                    self.log(f"⚠️ AI could not structure {filename}")
                    self.stats["failed"] += 1
                    
            except Exception as e:
                self.log(f"❌ Synthesis error for {filename}: {e}")
                self.stats["failed"] += 1

        self.log("\n" + "="*40)
        self.log("Ingestion Summary:")
        self.log(f"  Processed: {self.stats['processed']}")
        self.log(f"  Failed:    {self.stats['failed']}")
        self.log(f"  Skipped:   {self.stats['skipped']}")
        self.log("="*40)

if __name__ == "__main__":
    # Check dependencies and hint user
    missing = []
    if not HAS_DOCX: missing.append("python-docx")
    if not HAS_PDF: missing.append("pdfplumber")
    if not HAS_BS4: missing.append("beautifulsoup4")
    
    if missing:
        print("\n" + "!"*60)
        print("NOTICE: For full format support, please install missing libraries:")
        print(f"pip install {' '.join(missing)} tabulate")
        print("!"*60 + "\n")

    gateway = KnowledgeGateway()
    gateway.process_folder()
