import sqlite3
import json
import os
import sys

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def restore_raw_emails():
    db_path = 'emails.db'
    output_dir = 'raw/emails'
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database {db_path} not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM emails")
    total = cursor.fetchone()[0]
    print(f"Found {total} emails in database. Starting restoration...")

    cursor.execute("SELECT entry_id, subject, sender_name, sender_email, received_time, body, folder, has_attachments FROM emails")
    
    count = 0
    for row in cursor:
        entry_id, subject, sender_name, sender_email, received_time, body, folder, has_attachments = row
        
        # Build the same JSON structure expected by wiki_builder.py
        email_data = {
            "entry_id": entry_id,
            "subject": subject,
            "sender_name": sender_name,
            "sender_email": sender_email,
            "received_time": received_time,
            "body": body,
            "folder": folder,
            "has_attachments": bool(has_attachments)
        }
        
        # Use entry_id as filename (as wiki_builder expects)
        filename = f"{entry_id}.json"
        # Sanitize filename just in case entry_id has weird characters
        filename = "".join([c for c in filename if c.isalnum() or c in "._-"])
        if not filename.endswith(".json"): filename += ".json"
        
        path = os.path.join(output_dir, filename)
        
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                json.dump(email_data, f, ensure_ascii=False, indent=2)
            count += 1
            if count % 1000 == 0:
                print(f"Restored {count}/{total} emails...")
        except Exception as e:
            print(f"Error saving {filename}: {e}")

    conn.close()
    print(f"Restoration complete. {count} files created in {output_dir}.")

if __name__ == "__main__":
    restore_raw_emails()
