import os
import sqlite3
import traceback

# Mocking Flask environment
def jsonify(data): return data

def get_stats_standalone():
    try:
        db_path = 'emails.db'
        print(f"Connecting to: {os.path.abspath(db_path)}")
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT subject, sender_name, sender_email, received_time FROM emails ORDER BY received_time DESC LIMIT 10"
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
        print("SUCCESS: Stats data retrieved correctly.")
        return recent_data
    except Exception:
        print("FAILURE: Error in get_stats_standalone")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    get_stats_standalone()
