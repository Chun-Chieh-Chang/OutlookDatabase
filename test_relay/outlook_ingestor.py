#!/usr/bin/env python3
"""
Outlook Ingestor (SkillsBuilder Pro) v3.3 RECURSIVE ULTRA
Full-scale recursive extraction with noise filtering (Excluding Deleted/Junk).
"""

import win32com.client
import pythoncom
import sqlite3
import os
import sys
import io

# Fix Windows encoding for console output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_NAME = 'emails.db'

def init_storage():
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

def ingest_emails(max_total=500000):
    print(f"Starting SkillsBuilder RECURSIVE ULTRA Ingestor...")
    
    try:
        pythoncom.CoInitialize()
        outlook_app = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook_app.GetNamespace("MAPI")
        
        # Folder type constants
        SKIP_TYPES = [3, 23, 16, 21] 
        skip_entry_ids = []
        for st in SKIP_TYPES:
            try:
                folder = namespace.GetDefaultFolder(st)
                if folder: skip_entry_ids.append(folder.EntryID)
            except: pass

        try:
            default_store = namespace.DefaultStore
            root = default_store.GetRootFolder()
        except:
            root = namespace.Folders.Item(1)
        print(f"SYSTEM: Account Detected: {root.Name}")
        
        conn = init_storage()
        cursor = conn.cursor()
        
        state = {"new_count": 0, "processed": 0}

        def scan_folder(folder):
            # Skip if it's a deleted/junk folder
            if folder.EntryID in skip_entry_ids:
                return

            print(f"SCANNING: {folder.FolderPath}")
            
            try:
                items = folder.Items
                items.Sort("[ReceivedTime]", True)
                
                for msg in items:
                    try:
                        if msg.Class == 43: # MailItem
                            eid = msg.EntryID
                            cursor.execute("SELECT 1 FROM emails WHERE entry_id = ?", (eid,))
                            if cursor.fetchone(): 
                                continue
                                
                            subj = msg.Subject or "No Subject"
                            sender = msg.SenderName or msg.SenderEmailAddress or "Unknown"
                            body = msg.Body or ""
                            
                            try:
                                rt = msg.ReceivedTime
                                time_str = f"{rt.year}-{rt.month:02d}-{rt.day:02d} {rt.hour:02d}:{rt.minute:02d}:{rt.second:02d}"
                            except:
                                time_str = str(msg.ReceivedTime)
                            
                            cursor.execute("""
                                INSERT INTO emails (entry_id, subject, sender_name, received_time, body, folder)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (eid, subj, sender, time_str, body, folder.Name))
                            
                            state["new_count"] += 1
                            if state["new_count"] % 100 == 0:
                                print(f"  [SYNC] New: {state['new_count']} items found...")
                    except:
                        continue
                
                # Recursive call for sub-folders
                for sub in folder.Folders:
                    scan_folder(sub)
                    
            except Exception as e:
                print(f"  WARN: Skipping {folder.Name} due to {e}")

        # Start from the root folder of the account
        scan_folder(root)
        
        conn.commit()
        conn.close()
        
        print(f"\nSUCCESS: Synchronization Complete.")
        print(f"Total New Emails: {state['new_count']}")
            
    except Exception as e:
        print(f"ERROR: Ingestion failed: {e}")
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    ingest_emails()
