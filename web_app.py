import os
import requests
import sqlite3
import subprocess
import re
import json
import sys
import time
from tools.evolution_metrics import EvolutionAnalyzer
# Robust file reader for Windows environments (Multi-encoding fallback)
def safe_read_file(path):
    encodings = ['utf-8-sig', 'utf-8', 'cp950', 'big5']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    # Absolute Fallback
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

# Global Pipeline Manager
class PipelineManager:
    def __init__(self):
        self.current_process = None
    
    def run(self, cmd_args):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
        self.current_process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        return self.current_process

    def stop(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            return True
        return False

pipeline_mgr = PipelineManager()
from flask import Flask, request, jsonify, render_template, Response, stream_with_context, send_file, send_from_directory
from email_analyzer import EmailAnalyzer
from hermes_core import HermesAgent
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Initialize AI Analyzer & Hermes
ai_analyzer = None
ai_available = False
hermes = HermesAgent()

def init_ai():
    global ai_analyzer, ai_available
    try:
        ai_analyzer = EmailAnalyzer()
        ai_available = ai_analyzer.check_ollama_connection()
        print(f"AI Service Available: {ai_available} (Model: {ai_analyzer.model})")
    except Exception as e:
        print(f"AI Initialization Error: {e}")
        ai_available = False

init_ai()

def get_connection():
    return sqlite3.connect('emails.db')

def get_wiki_stats():
    """
    Standardized counter for QC 3.0 Knowledge Nodes.
    Ensures alignment between Dashboard and 3D Graph.
    """
    entity_count = 0
    concept_count = 0
    wiki_root = 'wiki'
    
    if os.path.exists(wiki_root):
        for root, dirs, files in os.walk(wiki_root):
            for f in files:
                # 排除非知識檔案
                if not f.endswith('.md') or f.lower() in ['index.md', 'log.md', 'extraction_pulse.txt']:
                    continue
                
                # 判斷是技術實體 (Spec/Part) 還是品質概念 (CAPA/NCA/Logic)
                path_lower = root.lower()
                if any(x in path_lower for x in ['capa', 'nca', 'iqc', 'pqc', 'oqc']):
                    concept_count += 1
                else:
                    # 包含 spec 與 根目錄下的實體
                    entity_count += 1
    return entity_count, concept_count

@app.route('/')
def index():
    db_exists = os.path.exists('emails.db')
    return render_template('index.html', 
                           db_exists_js='true' if db_exists else 'false',
                           v=int(time.time()))

@app.route('/api/dashboard_stats')
def dashboard_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT sender_name) FROM emails")
        unique_senders = cursor.fetchone()[0]
        conn.close()
        entity_count, concept_count = get_wiki_stats()
        return jsonify({
            'total_emails': total_emails,
            'unique_senders': unique_senders,
            'entity_count': entity_count,
            'concept_count': concept_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    import traceback
    try:
        # Use absolute path to ensure DB is found
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emails.db')
        conn = sqlite3.connect(db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT subject, sender_name, sender_email, received_time FROM emails WHERE received_time IS NOT NULL AND received_time != 'Unknown' ORDER BY received_time DESC LIMIT 10"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        recent_data = []
        for row in rows:
            name = row['sender_name']
            email = row['sender_email']
            display = name if name and name.strip() and name.lower() != 'unknown' else (email if email else '系統郵件')
            recent_data.append({
                'subject': row['subject'],
                'sender': display,
                'received_time': row['received_time']
            })
            
        return jsonify({'recent_emails': recent_data})
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"CRITICAL ERROR in /api/stats:\n{error_msg}")
        return jsonify({'error': str(e), 'traceback': error_msg}), 500

@app.route('/api/search', methods=['POST'])
def search_emails():
    data = request.get_json()
    query = data.get('keyword', '')
    page = data.get('page', 1)
    limit = data.get('limit', 20)
    offset = (page - 1) * limit
    
    # Smart Search: Detect if the query ends with a 4-digit year (Legacy support)
    # or use the explicit year parameter (New standard)
    year_filter = data.get('year')
    clean_query = query
    
    if not year_filter:
        words = query.split()
        if len(words) > 1 and words[-1].isdigit() and len(words[-1]) == 4:
            year_filter = words[-1]
            clean_query = " ".join(words[:-1])
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Base SQL
    where_clause = "(subject LIKE ? OR body LIKE ?)"
    params = [f'%{clean_query}%', f'%{clean_query}%']
    
    if year_filter:
        where_clause += " AND substr(received_time, 1, 4) = ?"
        params.append(year_filter)
        
    # Get total count
    count_sql = f"SELECT COUNT(*) FROM emails WHERE {where_clause}"
    cursor.execute(count_sql, params)
    total_count = cursor.fetchone()[0]
    
    # Get paginated results
    sql = f"SELECT subject, sender_name, received_time, body FROM emails WHERE {where_clause} ORDER BY received_time DESC LIMIT ? OFFSET ?"
    cursor.execute(sql, params + [limit, offset])
    rows = cursor.fetchall()
    results = [dict(zip([d[0] for d in cursor.description], row)) for row in rows]
    
    # Get year distribution (always based on clean query to show potential years)
    year_sql = "SELECT substr(received_time, 1, 4) as year, COUNT(*) FROM emails WHERE (subject LIKE ? OR body LIKE ?) GROUP BY year ORDER BY year DESC"
    cursor.execute(year_sql, [f'%{clean_query}%', f'%{clean_query}%'])
    year_dist = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        'results': results, 
        'count': len(results),
        'total_count': total_count,
        'year_distribution': year_dist,
        'page': page,
        'total_pages': max(1, (total_count + limit - 1) // limit)
    })



@app.route('/api/manual')
def get_manual():
    try:
        content = safe_read_file('SYSTEM_MANUAL.md')
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evolution')
def get_evolution():
    try:
        analyzer = EvolutionAnalyzer()
        return jsonify(analyzer.calculate_metrics())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_status')
def get_ai_status():
    global ai_available, ai_analyzer
    if ai_analyzer is None:
        init_ai()
    elif not ai_available:
        # If it was offline, actively check if it came back online
        ai_available = ai_analyzer.check_ollama_connection()
        
    return jsonify({'available': ai_available, 'model': ai_analyzer.model if ai_analyzer else 'N/A'})

@app.route('/api/ai_config', methods=['GET'])
def get_ai_config():
    try:
        config = json.loads(safe_read_file('ai_config.json'))
        # Hide actual API key for safety in UI (mask it)
        display_config = json.loads(json.dumps(config))
        if 'google' in display_config and display_config['google'].get('api_key'):
            key = display_config['google']['api_key']
            if len(key) > 8:
                display_config['google']['api_key'] = f"{key[:4]}...{key[-4:]}"
        return jsonify(display_config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_config_update', methods=['POST'])
def update_ai_config():
    global ai_analyzer, ai_available
    new_config = request.get_json()
    try:
        # Load existing to preserve fields or handle partial updates
        current_config = json.loads(safe_read_file('ai_config.json'))
        
        # If key is masked in UI, don't overwrite the real one
        if new_config.get('google', {}).get('api_key', '').count('.') > 0:
            new_config['google']['api_key'] = current_config.get('google', {}).get('api_key', '')
            
        current_config.update(new_config)
        
        with open('ai_config.json', 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2, ensure_ascii=False)
            
        # Re-initialize analyzer
        ai_analyzer = EmailAnalyzer()
        ai_available = ai_analyzer.check_ollama_connection()
        
        return jsonify({'message': 'Configuration updated', 'available': ai_available})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ollama_models')
def get_ollama_models():
    try:
        # 使用絕對路徑確保讀取正確
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai_config.json')
        if not os.path.exists(config_path):
            return jsonify({'models': [], 'error': 'Config file not found'})
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        url = config.get('ollama', {}).get('url', 'http://localhost:11434')
        try:
            resp = requests.get(f"{url}/api/tags", timeout=5)
            if resp.status_code == 200:
                return jsonify(resp.json())
            return jsonify({'models': [], 'error': f'Ollama returned status {resp.status_code}'})
        except requests.exceptions.ConnectionError:
            return jsonify({'models': [], 'error': 'Cannot connect to Ollama service'})
    except Exception as e:
        return jsonify({'models': [], 'error': str(e)})

@app.route('/api/ai_reconnect', methods=['POST'])
def ai_reconnect():
    global ai_available, ai_analyzer
    try:
        ai_analyzer = EmailAnalyzer()
        ai_available = ai_analyzer.check_ollama_connection()
        return jsonify({'available': ai_available, 'model': ai_analyzer.model, 'message': 'Reconnected'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/stop', methods=['POST'])
def pipeline_stop():
    success = pipeline_mgr.stop()
    return jsonify({'success': success, 'message': 'Pipeline stopped' if success else 'No active pipeline'})

@app.route('/api/pipeline/stream')
def pipeline_stream():
    def generate():
        python_exe = sys.executable
        yield "data: 🚀 啟動安全生產管道...\n\n"
        
        try:
            # Step 1: Ingest
            process = pipeline_mgr.run([python_exe, 'outlook_ingestor.py', '--limit', '100'])
            
            ingest_failed = False
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line: 
                    if "❌" in line or "failed" in line.lower(): ingest_failed = True
                    yield f"data: {line.strip()}\n\n"
                else: 
                    yield "data: heartbeat\n\n"
                    time.sleep(1)
            
            if ingest_failed:
                yield "data: ⚠️ 數據源讀取異常，將使用現有資料緩存...\n\n"
            
            # Step 2: Build Wiki
            yield "data: 🧠 啟動知識圖譜建構...\n\n"
            process = pipeline_mgr.run([python_exe, 'wiki_builder.py', '50'])
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None: break
                if line: yield f"data: {line.strip()}\n\n"
                else:
                    yield "data: heartbeat\n\n"
                    time.sleep(1)
            
            yield "data: ✅ 管道任務順利結束。\n\n"
        except GeneratorExit:
            pipeline_mgr.stop()
            print("Client disconnected, pipeline stopped.")
        except Exception as e:
            yield f"data: ❌ 發生非預期錯誤: {str(e)}\n\n"
        finally:
            pipeline_mgr.stop()
            
    resp = Response(stream_with_context(generate()), mimetype='text/event-stream')
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Connection'] = 'keep-alive'
    return resp

@app.route('/api/important_folders_ingest', methods=['POST'])
def run_important_ingest():
    data = request.get_json()
    max_per = data.get('max_per_folder', 100)
    try:
        subprocess.run([sys.executable, 'outlook_ingestor.py', '--limit', str(max_per)], check=True)
        return jsonify({'message': 'Success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/build_wiki', methods=['POST'])
def run_build_wiki():
    try:
        subprocess.run([sys.executable, 'wiki_builder.py', '50'], check=True)
        return jsonify({'message': 'Success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wiki/status')
def get_wiki_status():
    e_count, c_count = get_wiki_stats()
    status = 'built' if e_count > 0 else 'not_built'
    return jsonify({'status': status, 'entities': e_count, 'concepts': c_count})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/import_bundle', methods=['POST'])
def import_bundle():
    bundle_path = 'sync_bundle.db'
    if not os.path.exists(bundle_path):
        return jsonify({'error': '找不到 sync_bundle.db 檔案，請先將其複製到專案目錄。'}), 404
        
    try:
        main_conn = sqlite3.connect('emails.db')
        bundle_conn = sqlite3.connect(bundle_path)
        bundle_conn.row_factory = sqlite3.Row
        cursor = bundle_conn.cursor()
        cursor.execute("SELECT * FROM emails")
        rows = cursor.fetchall()
        
        # Prepare for insertion
        if rows:
            cols = rows[0].keys()
            placeholders = ",".join(["?"] * len(cols))
            insert_sql = f"INSERT INTO emails ({','.join(cols)}) VALUES ({placeholders})"
            main_conn.executemany(insert_sql, [tuple(row) for row in rows])
            main_conn.commit()
            
        main_conn.close()
        bundle_conn.close()
        return jsonify({'message': f'成功導入 {len(rows)} 封郵件數據！'})
    except Exception as e:
        return jsonify({'error': f'導入失敗: {str(e)}'}), 500

@app.route('/api/ask_wiki', methods=['POST'])
def ask_wiki():
    global ai_available, ai_analyzer
    if not ai_available or ai_analyzer is None: init_ai()
    if not ai_available or ai_analyzer is None: return jsonify({'error': 'AI 服務目前不可用'}), 503
    data = request.get_json()
    query = data.get('query')
    try:
        answer = ai_analyzer.query_knowledge_base(query)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graph_data')
def get_graph_data():
    graph_path = 'wiki/graph_data.json'
    if os.path.exists(graph_path):
        raw_data = json.loads(safe_read_file(graph_path))
        nodes = []
        node_ids = set()
        
        # Handle list of nodes
        # Handle list of nodes (v3.0 format)
        for node_data in raw_data.get('nodes', []):
            node_id = node_data.get('id')
            if not node_id: continue
            
            node_item = node_data.copy()
            node_item['group'] = node_data.get('type', 'general')
            nodes.append(node_item)
            node_ids.add(node_id)
        
        links = []
        for link in raw_data.get('links', []):
            if link['source'] in node_ids and link['target'] in node_ids:
                links.append({
                    'source': link['source'],
                    'target': link['target']
                })
        
        return jsonify({'nodes': nodes, 'links': links})
    return jsonify({'nodes': [], 'links': []})

@app.route('/api/wiki/index')
def get_wiki_index():
    wiki_root = os.path.abspath('wiki')
    if not os.path.exists(wiki_root): return jsonify({'content': '尚未建構'})
    
    md_files = []
    seen_titles = set()
    for root, dirs, files in os.walk(wiki_root):
        for f in files:
            if f.endswith('.md') and f.lower() not in ['index.md', 'log.md']:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, wiki_root).replace('\\', '/')
                display_name = f.replace('.md', '')
                try:
                    with open(full_path, 'r', encoding='utf-8') as content_f:
                        first_lines = content_f.readlines()[:10]
                        for line in first_lines:
                            if line.startswith('title:'):
                                display_name = line.replace('title:', '').strip().strip('"').strip("'")
                                break
                            if line.startswith('# '):
                                display_name = line.replace('# ', '').strip()
                                break
                except: pass
                if display_name not in seen_titles:
                    md_files.append(f"[{display_name}]({rel_path})")
                    seen_titles.add(display_name)
    
    if not md_files:
        idx = os.path.join(wiki_root, 'index.md')
        if os.path.exists(idx):
            return jsonify({'content': safe_read_file(idx)})
        return jsonify({'content': '目前尚無知識實體，請先執行掃描。'})
    
    md_files.sort()
    return jsonify({'content': '\n'.join(md_files)})

@app.route('/api/wiki/page/<path:path>')
def get_wiki_page(path):
    wiki_root = os.path.abspath('wiki')
    clean_path = path.replace('/', os.sep).replace('\\', os.sep).lstrip(os.sep)
    full_path = os.path.join(wiki_root, clean_path)
    
    # --- New: Check if path is actually an entry_id ---
    filename_only = os.path.basename(clean_path).replace('.md', '')
    if len(filename_only) > 24 and all(c in '0123456789ABCDEFabcdef' for c in filename_only):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT subject, sender_name, received_time, body FROM emails WHERE entry_id = ?", (filename_only,))
            row = cursor.fetchone()
            conn.close()
            if row:
                subject, sender, time, body = row
                content = f"# {subject}\n\n> 📧 **原始郵件線索**\n> **寄件者**: {sender}\n> **時間**: {time}\n\n---\n\n{body}"
                return jsonify({'content': content})
        except: pass

    if os.path.exists(full_path) and os.path.isfile(full_path):
        content = safe_read_file(full_path).strip()
        if content:
            return jsonify({'content': content})
            
    # Fallback: Try to find file by name or generate dynamic summary
    filename = os.path.basename(clean_path)
    entity_name = filename.replace('.md', '')
    # Try to find file in any subdirectory
    for root, dirs, files in os.walk(wiki_root):
        for f_in_dir in files:
            if f_in_dir.lower() == filename.lower():
                target_path = os.path.join(root, f_in_dir)
                content = safe_read_file(target_path).strip()
                if content:
                    return jsonify({'content': content, 'actual_path': target_path})

    # If still empty or not found, generate dynamic summary from DB
    from email_analyzer import EmailAnalyzer
    analyzer = EmailAnalyzer()
    db_summary = analyzer.get_entity_context(entity_name)
    
    if db_summary:
        header = f"# {entity_name} (動態檢索報告)\n\n> 💡 系統偵測到此實體的靜態文檔尚未完成，已為您從原始郵件庫中即時提取相關背景。\n\n"
        return jsonify({'content': header + db_summary})
                
    return jsonify({'error': f'找不到相關資訊: {entity_name}'}), 404

@app.route('/api/wiki/synthesize', methods=['POST'])
def synthesize_wiki():
    data = request.get_json()
    entity_name = data.get('entity_name')
    file_path = data.get('file_path') # e.g. "man/Abbie Tai.md"
    
    if not entity_name or not file_path:
        return jsonify({'error': 'Missing parameters'}), 400
        
    global ai_available, ai_analyzer
    if not ai_available or ai_analyzer is None: init_ai()
    if not ai_available or ai_analyzer is None: 
        return jsonify({'error': 'AI 服務目前離線，無法進行深度總結。請先啟動 Ollama。'}), 503
        
    try:
        db_summary = ai_analyzer.get_entity_context(entity_name)
        if not db_summary:
            return jsonify({'error': '在資料庫中找不到與此實體相關的足夠上下文。'}), 404
            
        full_path = os.path.join(os.path.abspath('wiki/dimensions'), file_path)
        if os.path.exists(full_path):
            content = safe_read_file(full_path)
            
            # Perform AI Synthesis first
            ai_report = ai_analyzer.synthesize_entity_report(entity_name, db_summary)
            
            # CRITICAL: Prevent saving error messages to the knowledge base
            if "錯誤" in ai_report or "timeout" in ai_report.lower() or "error" in ai_report.lower():
                return jsonify({'error': f'AI 合成逾時或失敗 (請檢查 Ollama 負載): {ai_report}'}), 502

            # Only if successful, update the file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Precise placeholder removal to avoid wiping the whole file
            content = re.sub(r'> \*\*實體驗證.*?\n\n', '', content)
            content = re.sub(r'歷史郵件出現次數: \*\*.*?\*\*。點擊或開啟它時，AI 能為您即時總結。\n?', '', content)
            content = re.sub(r'這是系統利用大數據特徵工程提取的知識節點.*?\n?', '', content)
            
            new_content = content.strip() + f"\n\n> 🧠 **AI 深度合成報告** (模型: {ai_analyzer.model})\n\n" + ai_report
            
            with open(full_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
                
            return jsonify({'message': 'Synthesis complete', 'new_content': new_content})
        else:
            return jsonify({'error': '實體檔案不存在'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dev_log')
def get_dev_log():
    try:
        content = safe_read_file('DEV_LOG.md')
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entities')
def get_entities():
    """
    Returns wiki entities grouped by dimension for the 'Knowledge Grouping' view.
    """
    grouped_entities = {}
    wiki_root = os.path.join('wiki', 'dimensions')
    
    if not os.path.exists(wiki_root):
        return jsonify({})

    for dimension in os.listdir(wiki_root):
        dim_path = os.path.join(wiki_root, dimension)
        if not os.path.isdir(dim_path):
            continue
            
        entities = []
        for f in os.listdir(dim_path):
            if f.endswith('.md') and f.lower() not in ['index.md', 'log.md', 'extraction_pulse.txt']:
                file_path = os.path.join(dim_path, f)
                
                # Extract first non-empty line as description
                description = ""
                try:
                    with open(file_path, 'r', encoding='utf-8') as content_f:
                        lines = content_f.readlines()
                        in_frontmatter = False
                        for line in lines:
                            line = line.strip()
                            if not line: continue
                            if line == '---':
                                in_frontmatter = not in_frontmatter
                                continue
                            if in_frontmatter: continue
                            if line.startswith('#'): continue
                            description = line
                            break
                except:
                    description = "點擊查看詳細工業知識..."

                entities.append({
                    'name': f.replace('.md', ''),
                    'path': f"{dimension}/{f}",
                    'category': dimension.upper(),
                    'description': (description[:100] + '...') if len(description) > 100 else description
                })
        
        if entities:
            grouped_entities[dimension.upper()] = entities
            
    return jsonify(grouped_entities)

@app.route('/api/hermes/status')
def get_hermes_status():
    hermes.load_state()
    return jsonify(hermes.state)

@app.route('/api/hermes/accumulate', methods=['POST'])
def run_hermes_accumulate():
    data = request.get_json() or {}
    limit = data.get('limit', 10)
    try:
        count = hermes.accumulate(limit=limit)
        return jsonify({'message': f'Hermes 成功處理了 {count} 封新郵件', 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wiki/batch_synthesize')
def batch_synthesize():
    def generate():
        global ai_analyzer, ai_available
        if not ai_analyzer: init_ai()
        if not ai_available:
            yield "data: ❌ AI 服務離線，請先啟動 Ollama\n\n"
            return

        yield "data: 🚀 啟動批次合成任務，正在掃描待處理實體...\n\n"
        
        wiki_root = os.path.abspath('wiki/dimensions')
        targets = []
        for root, dirs, files in os.walk(wiki_root):
            for f in files:
                if f.endswith('.md'):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        if "點擊或開啟它時，AI 能為您即時總結。" in content:
                            freq_match = re.search(r'歷史郵件出現次數: \*\*(\d+) 次\*\*', content)
                            freq = int(freq_match.group(1)) if freq_match else 0
                            targets.append({
                                'path': os.path.relpath(path, wiki_root).replace('\\', '/'),
                                'name': f.replace('.md', ''),
                                'freq': freq
                            })
                    except: pass
        
        targets.sort(key=lambda x: x['freq'], reverse=True)
        yield f"data: 發現 {len(targets)} 個待處理實體。按頻率排序開始...\n\n"
        
        for i, target in enumerate(targets):
            yield f"data: [{i+1}/{len(targets)}] 正在處理: {target['name']} (頻率: {target['freq']})...\n\n"
            try:
                db_summary = ai_analyzer.get_entity_context(target['name'])
                if db_summary:
                    ai_report = ai_analyzer.synthesize_entity_report(target['name'], db_summary)
                    if "錯誤" not in ai_report and "timeout" not in ai_report.lower():
                        full_path = os.path.join(wiki_root, target['path'])
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        content = re.sub(r'> \*\*實體驗證.*?\n\n', '', content)
                        content = re.sub(r'歷史郵件出現次數: \*\*.*?\*\*。點擊或開啟它時，AI 能為您即時總結。\n?', '', content)
                        content = re.sub(r'這是系統利用大數據特徵工程提取的知識節點.*?\n?', '', content)
                        
                        new_content = content.strip() + f"\n\n> 🧠 **AI 深度合成報告** (模型: {ai_analyzer.model})\n\n" + ai_report
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        yield f"data: ✅ {target['name']} 合成成功。\n\n"
                    else:
                        yield f"data: ⚠️ {target['name']} 合成超時，跳過。\n\n"
                else:
                    yield f"data: ℹ️ {target['name']} 無法獲取上下文，跳過。\n\n"
            except Exception as e:
                yield f"data: ❌ {target['name']} 異常: {str(e)}\n\n"
        
        yield "data: 🏁 批次合成任務結束。\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/<path:entry_id>')
def view_email_by_id(entry_id):
    # Check if it looks like a hex entry_id
    if len(entry_id) > 24 and all(c in '0123456789ABCDEFabcdef' for c in entry_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT subject, sender_name, received_time, body FROM emails WHERE entry_id = ?", (entry_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                subject, sender, time, body = row
                # Return a simple but clean HTML for the email
                return f"""
                <html>
                <head>
                    <title>{subject}</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
                    <style>
                        body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: #1e293b; padding: 40px; background: #f8fafc; }}
                        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
                        h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 24px; color: #0f172a; }}
                        .meta {{ font-size: 13px; color: #64748b; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #e2e8f0; }}
                        .body {{ white-space: pre-wrap; font-size: 15px; }}
                        .back {{ display: inline-block; margin-bottom: 20px; color: #3b82f6; text-decoration: none; font-weight: 600; font-size: 14px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <a href="/" class="back">← 返回儀表板</a>
                        <h1>{subject}</h1>
                        <div class="meta">
                            <strong>寄件者:</strong> {sender}<br>
                            <strong>日期:</strong> {time}
                        </div>
                        <div class="body">{body}</div>
                    </div>
                </body>
                </html>
                """
        except: pass
    
    return jsonify({'error': 'Page not found'}), 404

if __name__ == '__main__':
    init_ai()
    app.run(host='0.0.0.0', port=5000, debug=True)
