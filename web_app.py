#!/usr/bin/env python3
"""
Web interface for Outlook Database Tool
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import os
import subprocess
import json
from datetime import datetime
from email_analyzer import EmailAnalyzer

app = Flask(__name__)

# Initialize AI analyzer
try:
    ai_analyzer = EmailAnalyzer()
    ai_available = ai_analyzer.check_ollama_connection()
except:
    ai_analyzer = None
    ai_available = False

# Configuration
DB_NAME = 'emails.db'

# Extraction Plans
PLANS = {
    '1': {'name': '超快速測試', 'emails': 10, 'body_limit': 200},
    '2': {'name': '日常使用', 'emails': 50, 'body_limit': 500},
    '3': {'name': '完整更新', 'emails': 200, 'body_limit': 1000},
    '4': {'name': '完整匯入', 'emails': 500, 'body_limit': 2000}
}

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)

def check_database_exists():
    """Check if database exists and has data"""
    if not os.path.exists(DB_NAME):
        return False, "尚未發現資料庫，請先執行「資料同步」。"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emails")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            return False, "資料庫目前為空，請執行「資料同步」。"
        return True, f"Database contains {count} emails"
    except Exception as e:
        return False, f"Database error: {str(e)}"

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    """Main page"""
    db_exists, message = check_database_exists()
    return render_template('index.html', db_exists=db_exists, message=message, 
                         db_exists_js='true' if db_exists else 'false')

@app.route('/api/stats')
def get_stats():
    """Get email statistics"""
    try:
        conn = get_connection()
        
        # Total emails
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]
        
        # Top senders
        query = """
            SELECT sender_name, COUNT(*) as count
            FROM emails
            GROUP BY sender_name
            ORDER BY count DESC
            LIMIT 10
        """
        df_senders = pd.read_sql_query(query, conn)
        
        # Recent emails
        query = """
            SELECT subject, sender_name, received_time
            FROM emails
            ORDER BY received_time DESC
            LIMIT 10
        """
        df_recent = pd.read_sql_query(query, conn)
        
        conn.close()
        
        return jsonify({
            'total_emails': total_emails,
            'top_senders': df_senders.to_dict('records'),
            'recent_emails': df_recent.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/semantic_search', methods=['POST'])
def semantic_search_emails():
    """Semantic search emails using AI"""
    if not ai_available:
        return jsonify({'error': 'AI service not available. Please run setup_ai.py first.'}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        # Perform semantic search
        results = ai_analyzer.semantic_search(query, limit)
        
        # Convert to dict format
        results_dict = []
        for result in results:
            results_dict.append({
                'id': result['id'],
                'subject': result['subject'],
                'body': result['body'],
                'sender_name': result['sender_name'],
                'received_time': result['received_time'],
                'relevance_score': result.get('relevance_score', 0)
            })
        
        return jsonify({
            'results': results_dict,
            'count': len(results_dict),
            'query': query,
            'search_type': 'semantic'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET', 'POST'])
def search_emails():
    """Search emails"""
    if request.method == 'POST':
        # Handle POST request with JSON body
        data = request.get_json()
        query = data.get('keyword', '') if data else ''
        limit = data.get('limit', 20) if data else 20
    else:
        # Handle GET request with query parameters
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
        
    conn = get_connection()
    query_sql = """
        SELECT subject, sender_name, sender_email, received_time, body
        FROM emails
        WHERE subject LIKE ? OR body LIKE ?
        ORDER BY received_time DESC
        LIMIT ?
    """
    params = (f'%{query}%', f'%{query}%', limit)
    
    df = pd.read_sql_query(query_sql, conn, params=params)
    conn.close()
    
    return jsonify({
        'results': df.to_dict('records'),
        'count': len(df),
        'query': query
    })

@app.route('/api/generate_summary', methods=['POST'])
def generate_summary():
    """Generate email summary using AI"""
    if not ai_available:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        summary = ai_analyzer.summarize_email(subject, body, '')
        
        return jsonify({
            'summary': summary,
            'subject': subject
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract_key_info', methods=['POST'])
def extract_key_info():
    """Extract key information using AI"""
    if not ai_available:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        keywords = ai_analyzer.extract_keywords(subject, body)
        
        # 生成重點資訊
        prompt = f"Email: {subject}\nContent: {body[:300]}..."
        system_prompt = "Extract the most important information from this email. Respond in Chinese."
        key_points = ai_analyzer.call_ollama(prompt, system_prompt)
        
        return jsonify({
            'keywords': keywords,
            'key_points': key_points
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_reply', methods=['POST'])
def generate_reply():
    """Generate reply suggestions using AI"""
    if not ai_available:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        prompt = f"Original Email Subject: {subject}\nOriginal Email Content: {body}"
        system_prompt = "Generate professional reply suggestions for this email. Provide 2-3 different reply options in Chinese."
        
        reply_suggestions = ai_analyzer.call_ollama(prompt, system_prompt)
        
        return jsonify({
            'reply_suggestions': reply_suggestions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate_email', methods=['POST'])
def translate_email():
    """Translate email using AI"""
    if not ai_available:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        body = data.get('body', '')
        target_lang = data.get('target_language', '英文')
        
        prompt = f"Please translate the following email to {target_lang}:\n\nSubject: {subject}\n\nContent: {body}"
        system_prompt = f"You are a professional translator. Translate the given email to {target_lang}. Provide the translation in this format:\nTranslated Subject: [translated subject]\nTranslated Content: [translated content]"
        
        translation = ai_analyzer.call_ollama(prompt, system_prompt)
        
        # 解析翻譯結果
        if "Translated Subject:" in translation and "Translated Content:" in translation:
            lines = translation.split('\n')
            translated_subject = ""
            translated_body = ""
            
            for line in lines:
                if line.strip().startswith("Translated Subject:"):
                    translated_subject = line.replace("Translated Subject:", "").strip()
                elif line.strip().startswith("Translated Content:"):
                    translated_body = line.replace("Translated Content:", "").strip()
        else:
            # 如果格式不正確，使用簡單分割
            translated_subject = f"[{target_lang}] {subject}"
            translated_body = f"[{target_lang}] {body}"
        
        return jsonify({
            'translated_subject': translated_subject,
            'translated_body': translated_body,
            'target_language': target_lang
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/email_insights', methods=['POST'])
def email_insights():
    """Generate email insights using AI"""
    if not ai_available:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        conn = get_connection()
        
        # 獲取基本統計
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]
        
        cursor.execute("SELECT sender_name, COUNT(*) as count FROM emails GROUP BY sender_name ORDER BY count DESC LIMIT 5")
        top_senders = cursor.fetchall()
        
        cursor.execute("SELECT strftime('%Y-%m', received_time) as month, COUNT(*) as count FROM emails GROUP BY month ORDER BY month DESC LIMIT 6")
        monthly_trend = cursor.fetchall()
        
        conn.close()
        
        # 生成洞察報告
        prompt = f"""
Email Statistics:
- Total emails: {total_emails}
- Top senders: {top_senders}
- Monthly trend: {monthly_trend}

Please analyze these email patterns and provide insights about communication trends, important topics, and recommendations.
"""
        system_prompt = "You are an email analytics expert. Analyze the email statistics and provide actionable insights in Chinese."
        
        insights = ai_analyzer.call_ollama(prompt, system_prompt)
        
        return jsonify({
            'insights': insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_database', methods=['POST'])
def clear_database():
    """Clear all emails from database"""
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # 獲取刪除前的郵件數量
        c.execute("SELECT COUNT(*) FROM emails")
        count_before = c.fetchone()[0]
        
        # 刪除所有郵件資料
        c.execute("DELETE FROM emails")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Database cleared successfully',
            'deleted_count': count_before
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_search_results', methods=['POST'])
def export_search_results():
    """Export search results to CSV"""
    try:
        data = request.get_json()
        search_results = data.get('search_results', [])
        search_query = data.get('search_query', 'search')
        
        if not search_results:
            return jsonify({'error': 'No search results to export'}), 400
        
        # Convert search results to DataFrame
        df = pd.DataFrame(search_results)
        
        # Generate filename with search query and timestamp
        filename = f'search_results_{search_query}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_emails():
    """Export emails to CSV"""
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM emails", conn)
        conn.close()
        
        filename = f'email_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/build_database_plan', methods=['POST'])
def build_database_plan():
    """Trigger database building with specific plan"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id', '2')  # Default to plan 2
        
        # Get plan configuration
        plan = PLANS.get(plan_id, PLANS['2'])  
        
        if plan_id == '5':  # Custom plan
            return jsonify({'error': 'Custom plan should use /api/build_database_custom endpoint'}), 400
        
        email_count = plan['emails']
        body_limit = plan['body_limit']
        
        # Run extraction with plan settings
        import outlook_ingestor
        outlook_ingestor.ingest_emails(max_emails=email_count, body_limit=body_limit)
        
        return jsonify({
            'message': f'Plan {plan_id} completed',
            'extracted_count': email_count,
            'plan_name': plan['name']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/build_database_custom', methods=['POST'])
def build_database_custom():
    """Trigger database building with custom settings"""
    try:
        data = request.get_json()
        email_count = data.get('email_count', 50)
        body_limit = data.get('body_limit', 200)
        
        # Validate inputs
        if email_count < 1 or email_count > 1000:
            return jsonify({'error': 'Email count must be between 1 and 1000'}), 400
        
        # Run extraction with custom settings
        import outlook_ingestor
        outlook_ingestor.ingest_emails(max_emails=email_count, body_limit=body_limit)
        
        return jsonify({
            'message': 'Custom extraction completed',
            'extracted_count': email_count,
            'email_count': email_count,
            'body_limit': body_limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/build_database', methods=['POST'])
def build_database():
    """Trigger database building"""
    try:
        import outlook_ingestor
        outlook_ingestor.ingest_emails(max_emails=50)
        return jsonify({'message': 'Database building completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_analyze', methods=['POST'])
def ai_analyze_emails():
    """AI analyze emails"""
    if not ai_available:
        return jsonify({'error': 'AI service not available. Please run setup_ai.py first.'}), 503
    
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        
        if not email_ids:
            return jsonify({'error': 'No email IDs provided'}), 400
        
        # Perform AI analysis
        results = ai_analyzer.analyze_email_batch(email_ids)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'report': ai_analyzer.generate_report(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai_status')
def get_ai_status():
    """Get AI service status"""
    return jsonify({
        'available': ai_available,
        'model': ai_analyzer.model if ai_analyzer else None,
        'service_url': ai_analyzer.base_url if ai_analyzer else None
    })

@app.route('/api/ingest', methods=['POST'])
def run_ingest():
    """Run the SkillsBuilder Ingestor"""
    try:
        # Run outlook_ingestor.py
        result = subprocess.run(['python', 'outlook_ingestor.py'], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return jsonify({'message': 'Ingest complete', 'output': result.stdout})
        else:
            return jsonify({'error': 'Ingest failed', 'details': result.stderr}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/build_wiki', methods=['POST'])
def run_build_wiki():
    """Run the Wiki Builder"""
    try:
        result = subprocess.run(['python', 'wiki_builder.py'], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return jsonify({'message': 'Wiki build complete', 'output': result.stdout})
        else:
            return jsonify({'error': 'Wiki build failed', 'details': result.stderr}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/full_pipeline', methods=['POST'])
def run_full_pipeline():
    """Run Ingest + Wiki Builder sequentially"""
    try:
        # Step 1: Ingest
        ingest_result = subprocess.run(['python', 'outlook_ingestor.py'], capture_output=True, text=True, encoding='utf-8')
        if ingest_result.returncode != 0:
            return jsonify({'error': 'Ingest stage failed', 'details': ingest_result.stderr}), 500
            
        # Step 2: Build Wiki
        wiki_result = subprocess.run(['python', 'wiki_builder.py'], capture_output=True, text=True, encoding='utf-8')
        if wiki_result.returncode != 0:
            return jsonify({'error': 'Wiki build stage failed', 'details': wiki_result.stderr}), 500
            
        return jsonify({
            'message': 'Full pipeline complete!',
            'ingest_output': ingest_result.stdout,
            'wiki_output': wiki_result.stdout
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wiki/index')
def get_wiki_index():
    """Get the Wiki index"""
    index_path = 'wiki/index.md'
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return jsonify({'content': f.read()})
    return jsonify({'content': '# Wiki index not found\nPlease run Build Wiki first.'})

@app.route('/api/wiki/page/<path:page_path>')
def get_wiki_page(page_path):
    """Get a specific Wiki page"""
    # Security: limit path to wiki folder
    full_path = os.path.join('wiki', page_path)
    if not full_path.endswith('.md'):
        full_path += '.md'
        
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return jsonify({'content': f.read()})
    return jsonify({'error': 'Page not found'}), 404

@app.route('/api/attachments/<entry_id>/<filename>')
def get_attachment(entry_id, filename):
    """Serve an attachment"""
    # Security: sanitize filename/entry_id
    # Use a simpler regex for security
    import re
    safe_entry_id = re.sub(r'[^a-zA-Z0-9_-]', '', entry_id)
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    path = os.path.join('raw/attachments', safe_entry_id, safe_filename)
    if os.path.exists(path):
        return send_file(path)
    return jsonify({'error': 'Attachment not found'}), 404

@app.route('/api/ask_wiki', methods=['POST'])
def ask_wiki():
    """Ask a question to the knowledge base (RAG)"""
    if not ai_available:
        return jsonify({'error': 'AI service not available'}), 503
        
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
        
    try:
        answer = ai_analyzer.query_knowledge_base(query)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
