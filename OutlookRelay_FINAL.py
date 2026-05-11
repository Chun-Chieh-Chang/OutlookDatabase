import os
import sys
import time
import sqlite3
import win32com.client
import pythoncom
import io
from datetime import datetime

# ==========================================
# Mouldex Relay ULTRA v3.5 - Core Logic
# Senior Architect Edition (Robustness & Aesthetics)
# ==========================================

# Force UTF-8 Output for Windows Console Defense
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def print_header():
    print("="*60)
    print("   MOULDEX RELAY ULTRA v3.5 - INDUSTRIAL DATA PIPELINE")
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
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
        except Exception as e:
            print(f"❌ [CRITICAL] Could not connect to Outlook: {e}")
            print("   Please ensure Outlook is installed and not running as Administrator if this tool is not.")
            time.sleep(5)
            return

        # Folder type constants to skip
        SKIP_TYPES = [3, 23, 16, 21] # Deleted, Junk, Drafts, etc.
        skip_entry_ids = []
        for st in SKIP_TYPES:
            try:
                f = namespace.GetDefaultFolder(st)
                if f: skip_entry_ids.append(f.EntryID)
            except: pass

        # Get Root Account
        try:
            root = namespace.DefaultStore.GetRootFolder()
        except:
            root = namespace.Folders.Item(1)
            
        print(f"✅ [SYSTEM] Account Linked: {root.Name}")
        print(f"[INFO] Preparing Local Storage: {DB_NAME}")
        
        conn = init_db(DB_NAME)
        cursor = conn.cursor()
        
        state = {"new": 0, "scanned": 0}

        def scan_recursive(folder):
            if folder.EntryID in skip_entry_ids:
                return

            print(f"📂 SCANNING: {folder.FolderPath}", end='\r')
            sys.stdout.flush()
            
            try:
                items = folder.Items
                items.Sort("[ReceivedTime]", True)
                
                # Limit scan to prevent hanging on huge folders (Industrial Safety)
                count = 0
                for msg in items:
                    count += 1
                    if count > 5000: break # Safety break
                    
                    try:
                        if msg.Class == 43: # MailItem
                            eid = msg.EntryID
                            
                            # Check if exists
                            cursor.execute("SELECT 1 FROM emails WHERE entry_id = ?", (eid,))
                            if cursor.fetchone():
                                continue
                                
                            subj = msg.Subject or "No Subject"
                            sender = msg.SenderName or "Unknown"
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
                            
                            state["new"] += 1
                            if state["new"] % 50 == 0:
                                print(f"✨ [PROGRESS] Extracted {state['new']} new items...      ", end='\r')
                                sys.stdout.flush()
                    except:
                        continue
                
                # Subfolders
                for sub in folder.Folders:
                    scan_recursive(sub)
                    
            except Exception as e:
                pass # Silently skip protected folders

        print("[START] Deep scanning knowledge nodes...")
        scan_recursive(root)
        conn.commit()
        
        print(f"\n\n📊 [RESULTS] Sync complete. New entries: {state['new']}")
        
        # Bundle for Relay
        print(f"[PACK] Creating Relay Bundle: {BUNDLE_NAME}...")
        conn.close()
        
        import shutil
        try:
            shutil.copy2(DB_NAME, BUNDLE_NAME)
            print(f"📦 [SUCCESS] Bundle ready for transfer.")
        except Exception as e:
            print(f"⚠️ [WARN] Could not create bundle: {e}")

        print("\n" + "="*60)
        print("   MISSION ACCOMPLISHED. SYSTEM STABLE.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ [CRITICAL ERROR] {str(e)}")
    finally:
        pythoncom.CoUninitialize()
        print("\nPress any key to exit...")
        # Simple wait for user (prevent auto-close if double-clicked)
        try:
            # We use input() but in some cases it might fail if stdin is redirected
            # For EXE it should work fine.
            input()
        except:
            pass

if __name__ == "__main__":
    relay_main()
