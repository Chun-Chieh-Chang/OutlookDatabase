import os
import sys
import time
import sqlite3
import win32com.client
import pythoncom
import io
from datetime import datetime

# ==========================================
# Mouldex Relay ULTRA v3.8 - Core Logic
# Stable Multi-Store Industrial Engine
# ==========================================

# Force UTF-8 Output for Windows Console Defense
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def print_header():
    print("="*60)
    print("   MOULDEX RELAY ULTRA v3.8 - INDUSTRIAL DATA PIPELINE")
    print("="*60)
    print(f"   Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Status:      INITIALIZING...")
    print("="*60)
    sys.stdout.flush()

def init_db(db_path):
    conn = sqlite3.connect(db_path)
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

def relay_main():
    print_header()
    
    DB_NAME = 'emails.db'
    BUNDLE_NAME = 'sync_bundle.db'
    
    try:
        print("[INFO] Connecting to Outlook MAPI Engine...")
        sys.stdout.flush()
        
        pythoncom.CoInitialize()
        try:
            # Revert to stable Dispatch method
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook_app.GetNamespace("MAPI")
        except Exception as e:
            print(f"❌ [CRITICAL] Connection Failed: {e}")
            time.sleep(5)
            return

        print(f"✅ [SYSTEM] Session Active: {namespace.CurrentUser}")

        conn = init_db(DB_NAME)
        cursor = conn.cursor()
        
        state = {"new": 0, "folders": 0}

        def scan_recursive(folder):
            state["folders"] += 1
            path = folder.FolderPath
            
            try:
                items = folder.Items
                count = items.Count
                print(f"📂 [{state['folders']}] {path} ({count})      ", end='\r')
                sys.stdout.flush()
                
                if count > 0:
                    # Scan from newest to oldest
                    limit = min(count, 50000)
                    for i in range(count, count - limit, -1):
                        try:
                            msg = items.Item(i)
                            if msg.Class not in [43, 46, 53]: continue
                            
                            eid = msg.EntryID
                            cursor.execute("SELECT 1 FROM emails WHERE entry_id = ?", (eid,))
                            if cursor.fetchone(): continue
                            
                            subj = getattr(msg, 'Subject', 'No Subject')
                            sender = getattr(msg, 'SenderName', 'Unknown')
                            body = getattr(msg, 'Body', '')
                            
                            try:
                                rt = msg.ReceivedTime
                                time_str = f"{rt.year}-{rt.month:02d}-{rt.day:02d} {rt.hour:02d}:{rt.minute:02d}:{rt.second:02d}"
                            except:
                                time_str = "Unknown"
                            
                            cursor.execute("""
                                INSERT INTO emails (entry_id, subject, sender_name, received_time, body, folder)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (eid, subj, sender, time_str, body, folder.Name))
                            
                            state["new"] += 1
                            if state["new"] % 25 == 0:
                                print(f"✨ [PROGRESS] Found {state['new']} records...      ", end='\r')
                                sys.stdout.flush()
                                if state["new"] % 250 == 0: conn.commit()
                        except:
                            continue
                
                # Subfolders
                if folder.Folders.Count > 0:
                    for sub in folder.Folders:
                        scan_recursive(sub)
            except:
                pass

        print("[START] Comprehensive Storage Scan...")
        
        # Iterate all stores to find hidden archives or shared mailboxes
        for store in namespace.Stores:
            try:
                print(f"\n📦 MOUNTING: {store.DisplayName}")
                root = store.GetRootFolder()
                scan_recursive(root)
                conn.commit()
            except:
                continue

        print(f"\n\n📊 [RESULTS] Sync complete. New entries: {state['new']}")
        conn.close()
        
        # Bundle
        import shutil
        try:
            if os.path.exists(BUNDLE_NAME): os.remove(BUNDLE_NAME)
            shutil.copy2(DB_NAME, BUNDLE_NAME)
            mb = os.path.getsize(BUNDLE_NAME) / (1024*1024)
            print(f"📦 [SUCCESS] Bundle ready ({mb:.2f} MB).")
        except:
            print("⚠️ Bundle copy failed.")

        print("\n" + "="*60)
        print("   MISSION ACCOMPLISHED. SYSTEM STABLE.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ [CRITICAL] {e}")
    finally:
        pythoncom.CoUninitialize()
        print("\nPress ENTER to exit...")
        try: input()
        except: pass

if __name__ == "__main__":
    relay_main()
