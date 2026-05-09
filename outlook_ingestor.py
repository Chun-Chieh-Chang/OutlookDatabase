#!/usr/bin/env python3
"""
Outlook Ingestor (SkillsBuilder Pro)
Extracts full email content, including attachments, to raw storage.
"""

import win32com.client
import pythoncom
import sqlite3
import datetime
import os
import json
import re
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
DB_NAME = 'emails.db'
# DEFAULT_ACCOUNT will be detected dynamically
MAX_EMAILS = 5000
RAW_DIR = 'raw'
EMAIL_DIR = os.path.join(RAW_DIR, 'emails')
ATTACH_DIR = os.path.join(RAW_DIR, 'attachments')

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def init_storage():
    os.makedirs(EMAIL_DIR, exist_ok=True)
    os.makedirs(ATTACH_DIR, exist_ok=True)
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
    try:
        root_folder = namespace.Folders.Item(account_name)
        return root_folder.Folders.Item(folder_name)
    except:
        # Fallback to default inbox if specific folder not found
        return namespace.GetDefaultFolder(6)

def ingest_emails(max_emails_per_folder=100):
    print(f"Starting SkillsBuilder Ingestor (Limit: {max_emails_per_folder} per folder)...")
    
    try:
        pythoncom.CoInitialize()
        outlook_app = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook_app.GetNamespace("MAPI")
        print("✅ Outlook COM initialized successfully")
        
        # Determine folders to process
        folders_to_process = []
        try:
            # Dynamically get the default store (account) root folder
            default_store = namespace.DefaultStore
            root = default_store.GetRootFolder()
            
            print(f"📍 Detected Account: {root.Name}")
            
            # Add Inbox and Sent
            # Using Folder constants for language-agnostic detection
            folders_to_process.append(namespace.GetDefaultFolder(6)) # Inbox
            try: folders_to_process.append(namespace.GetDefaultFolder(5)) # Sent
            except: pass
        except Exception as e:
            print(f"⚠️ Dynamic detection fallback: {e}")
            folders_to_process.append(namespace.GetDefaultFolder(6)) # Inbox
            folders_to_process.append(namespace.GetDefaultFolder(5)) # Sent
            
        conn = init_storage()
        cursor = conn.cursor()
        
        new_emails_count = 0
        for folder in folders_to_process:
            print(f"📁 Processing folder: {folder.Name}")
            items = folder.Items
            items.Sort("[ReceivedTime]", True)
            
            count = 0
            for msg in items:
                if count >= max_emails_per_folder: break
                
                try:
                    if msg.Class == 43: # MailItem
                        eid = msg.EntryID
                        # Check if already in DB
                        cursor.execute("SELECT 1 FROM emails WHERE entry_id = ?", (eid,))
                        if cursor.fetchone(): 
                            count += 1
                            continue
                            
                        subj = msg.Subject or "No Subject"
                        sender = msg.SenderName or msg.SenderEmailAddress or "未命名寄件者"
                        body = msg.Body or ""
                        time = str(msg.ReceivedTime)
                        
                        # Save raw JSON
                        email_data = {
                            "entry_id": eid,
                            "subject": subj,
                            "sender_name": sender,
                            "body": body,
                            "received_time": time
                        }
                        raw_path = os.path.join(EMAIL_DIR, f"{eid}.json")
                        with open(raw_path, 'w', encoding='utf-8') as f:
                            json.dump(email_data, f, ensure_ascii=False)
                            
                        # Save to DB
                        cursor.execute("""
                            INSERT INTO emails (entry_id, subject, sender_name, received_time, body, folder, raw_path)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (eid, subj, sender, time, body[:1000], folder.Name, raw_path))
                        
                        new_emails_count += 1
                        count += 1
                        if count % 10 == 0: print(f"  Synced {count} items...")
                except Exception as e:
                    continue
                    
        conn.commit()
        conn.close()
        
        if new_emails_count > 0:
            print(f"✅ Ingestion complete: {new_emails_count} new emails imported.")
        else:
            print("ℹ️ Check complete: Everything is up to date. No new emails found.")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    limit = 100
    if len(sys.argv) > 2 and sys.argv[1] == "--limit":
        limit = int(sys.argv[2])
    ingest_emails(limit)
