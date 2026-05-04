#!/usr/bin/env python3
"""
Outlook Ingestor (SkillsBuilder Pro)
Extracts full email content, including attachments, to raw storage.
"""

import win32com.client
import sqlite3
import datetime
import os
import json
import re

import sys

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
DB_NAME = 'emails.db'
FOLDER_NAME = '收件匣'
ACCOUNT_NAME = 'mike.chen@mouldex.com.tw'  
MAX_EMAILS = 5000  # Increased for full ingestion
RAW_DIR = 'raw'
EMAIL_DIR = os.path.join(RAW_DIR, 'emails')
ATTACH_DIR = os.path.join(RAW_DIR, 'attachments')

def clean_filename(filename):
    """Clean filename for OS storage."""
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def init_storage():
    """Ensure raw storage directories exist."""
    os.makedirs(EMAIL_DIR, exist_ok=True)
    os.makedirs(ATTACH_DIR, exist_ok=True)
    
    # Init DB as well for indexing
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            entry_id TEXT PRIMARY KEY,
            subject TEXT,
            sender_name TEXT,
            sender_email TEXT,
            received_time TEXT,
            body TEXT,
            folder TEXT,
            has_attachments INTEGER DEFAULT 0,
            raw_path TEXT
        )
    ''')
    conn.commit()
    return conn

def get_outlook_folder(namespace, account_name, folder_name):
    """Get the specific Outlook folder."""
    try:
        root_folder = namespace.Folders.Item(account_name)
        folder = root_folder.Folders.Item(folder_name)
        return folder
    except Exception as e:
        print(f"Error accessing folder {folder_name}: {e}")
        return None

def ingest_emails(max_emails=None, body_limit=None):
    """Extract and store everything from Outlook."""
    global MAX_EMAILS
    if max_emails is not None:
        MAX_EMAILS = max_emails
        
    print(f"Starting SkillsBuilder Ingestor (Limit: {MAX_EMAILS})...")
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        print(f"❌ Failed to connect to Outlook: {e}")
        return

    inbox = get_outlook_folder(outlook, ACCOUNT_NAME, FOLDER_NAME)
    if not inbox:
        print(f"❌ Could not find inbox for {ACCOUNT_NAME}")
        return
        
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)
    
    conn = init_storage()
    c = conn.cursor()
    
    print(f"📊 Processing top {MAX_EMAILS} emails from {inbox.Name}...")
    
    count = 0
    new_count = 0
    
    for msg in messages:
        if count >= MAX_EMAILS:
            break
            
        try:
            if msg.Class == 43:  # MailItem
                entry_id = msg.EntryID
                subject = msg.Subject
                sender_name = msg.SenderName
                sender_email = "Unknown"
                try:
                    sender_email = msg.SenderEmailAddress
                except: pass
                
                received_time = str(msg.ReceivedTime)
                body = msg.Body if msg.Body else ""
                
                if body_limit and len(body) > body_limit:
                    body = body[:body_limit] + "..."
                
                # Check attachments
                attachments = []
                has_attachments = 0
                if msg.Attachments.Count > 0:
                    has_attachments = 1
                    msg_attach_dir = os.path.join(ATTACH_DIR, clean_filename(entry_id))
                    os.makedirs(msg_attach_dir, exist_ok=True)
                    
                    for i in range(1, msg.Attachments.Count + 1):
                        attachment = msg.Attachments.Item(i)
                        filename = clean_filename(attachment.FileName)
                        save_path = os.path.join(msg_attach_dir, filename)
                        attachment.SaveAsFile(os.path.abspath(save_path))
                        attachments.append({
                            'filename': filename,
                            'path': save_path,
                            'size': attachment.Size
                        })
                
                # Metadata for JSON
                email_data = {
                    'entry_id': entry_id,
                    'subject': subject,
                    'sender_name': sender_name,
                    'sender_email': sender_email,
                    'received_time': received_time,
                    'body': body,
                    'folder': inbox.Name,
                    'attachments': attachments,
                    'ingested_at': datetime.datetime.now().isoformat()
                }
                
                # Save to RAW JSON
                json_filename = clean_filename(entry_id) + ".json"
                json_path = os.path.join(EMAIL_DIR, json_filename)
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(email_data, f, indent=2, ensure_ascii=False)
                
                # Update DB Index
                c.execute("SELECT 1 FROM emails WHERE entry_id = ?", (entry_id,))
                if c.fetchone() is None:
                    c.execute('''
                        INSERT INTO emails (entry_id, subject, sender_name, sender_email, received_time, body, folder, has_attachments, raw_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (entry_id, subject, sender_name, sender_email, received_time, body, inbox.Name, has_attachments, json_path))
                    new_count += 1
                else:
                    # Update existing record
                    c.execute('''
                        UPDATE emails 
                        SET subject=?, sender_name=?, sender_email=?, received_time=?, body=?, has_attachments=?, raw_path=?
                        WHERE entry_id=?
                    ''', (subject, sender_name, sender_email, received_time, body, has_attachments, json_path, entry_id))
                
                count += 1
                if count % 10 == 0:
                    print(f"✅ Ingested {count} emails...")
                    conn.commit()
                    
        except Exception as e:
            print(f"⚠️ Error processing email: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"✨ Ingest complete. Total: {count}, New: {new_count}")

if __name__ == "__main__":
    ingest_emails()
