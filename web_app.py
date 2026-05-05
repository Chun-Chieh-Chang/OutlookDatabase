import os
import requests
import sqlite3
import json
import pandas as pd
import subprocess
import sys
import time
from flask import Flask, request, jsonify, render_template, Response, stream_with_context, send_file
from email_analyzer import EmailAnalyzer
from datetime import datetime

app = Flask(__name__)

# Initialize AI Analyzer
ai_analyzer = None
ai_available = False

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
    entities_dir = 'wiki/entities'
    concepts_dir = 'wiki/concepts'
    e_count = 0
    c_count = 0
    if os.path.exists(entities_dir):
        e_count = len([f for f in os.listdir(entities_dir) if f.endswith('.md')])
    if os.path.exists(concepts_dir):
        c_count = len([f for f in os.listdir(concepts_dir) if f.endswith('.md')])
    return e_count, c_count

@app.route('/')
def index():
    db_exists = os.path.exists('emails.db')
    return render_template('index.html', db_exists_js='true' if db_exists else 'false')

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
    try:
        conn = get_connection()
        query = "SELECT subject, sender_name, received_time FROM emails ORDER BY received_time DESC LIMIT 10"
        df_recent = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify({'recent_emails': df_recent.to_dict('records')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_emails():
    data = request.get_json()
    query = data.get('keyword', '')
    page = data.get('page', 1)
    limit = data.get('limit', 20)
    offset = (page - 1) * limit
    
    if not query: return jsonify({'error': 'Query required'}), 400
    
    conn = get_connection()
    # Get total count first
    count_sql = "SELECT COUNT(*) FROM emails WHERE subject LIKE ? OR body LIKE ?"
    cursor = conn.cursor()
    cursor.execute(count_sql, (f'%{query}%', f'%{query}%'))
    total_count = cursor.fetchone()[0]
    
    # Get paginated results
    sql = "SELECT subject, sender_name, received_time, body FROM emails WHERE subject LIKE ? OR body LIKE ? ORDER BY received_time DESC LIMIT ? OFFSET ?"
    df = pd.read_sql_query(sql, conn, params=(f'%{query}%', f'%{query}%', limit, offset))
    conn.close()
    
    return jsonify({
        'results': df.to_dict('records'), 
        'count': len(df),
        'total_count': total_count,
        'page': page,
        'total_pages': (total_count + limit - 1) // limit
    })

@app.route('/api/ask_wiki', methods=['POST'])
def ask_wiki():
    if not ai_available: return jsonify({'error': 'AI Offline'}), 503
    data = request.get_json()
    query = data.get('query')
    try:
        answer = ai_analyzer.query_knowledge_base(query)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_status')
def get_ai_status():
    global ai_available, ai_analyzer
    return jsonify({'available': ai_available, 'model': ai_analyzer.model if ai_analyzer else 'N/A'})

@app.route('/api/ai_config', methods=['GET'])
def get_ai_config():
    try:
        with open('ai_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
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
        with open('ai_config.json', 'r', encoding='utf-8') as f:
            current_config = json.load(f)
        
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

@app.route('/api/pipeline/stream')
def pipeline_stream():
    def generate():
        python_exe = sys.executable
        
        # Step 1: Ingest
        yield "data: 🚀 啟動郵件同步程序...\n\n"
        process = subprocess.Popen([python_exe, 'outlook_ingestor.py', '--limit', '100'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        
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
            yield "data: ⚠️ 郵件同步未完全成功（可能是因為使用新版 Outlook），將直接使用現有資料建構知識圖譜...\n\n"
        
        # Step 2: Build Wiki
        yield "data: 🧠 啟動 AI 知識圖譜建構...\n\n"
        process = subprocess.Popen([python_exe, 'wiki_builder.py', '50'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None: break
            if line: yield f"data: {line.strip()}\n\n"
            else:
                yield "data: heartbeat\n\n"
                time.sleep(2)
        
        yield "data: ✅ 全流程執行成功！\n\n"
        
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

@app.route('/api/wiki/index')
def get_wiki_index():
    index_path = 'wiki/index.md'
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return jsonify({'content': f.read()})
    return jsonify({'content': '尚未建構'})

@app.route('/api/wiki/page/<path:path>')
def get_wiki_page(path):
    full_path = os.path.join('wiki', path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return jsonify({'content': f.read()})
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    # 關閉 debug 模式以提升串流穩定性
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
