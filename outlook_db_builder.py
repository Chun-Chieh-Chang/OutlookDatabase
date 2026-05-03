import win32com.client
import sqlite3
import datetime
import os

# Configuration
DB_NAME = 'emails.db'
FOLDER_NAME = '收件匣'  # 修正為中文收件匣名稱
ACCOUNT_NAME = 'mike.chen@mouldex.com.tw'  # 您的郵件帳號
MAX_EMAILS = 100  # 減少到 100 封，速度更快

def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
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
            folder TEXT
        )
    ''')
    conn.commit()
    return conn

def get_outlook_folder(namespace, account_name, folder_name):
    """Get the specific Outlook folder from the correct account."""
    try:
        # 獲取指定帳號的根資料夾
        root_folder = namespace.Folders.Item(account_name)
        
        # 獲取指定資料夾
        folder = root_folder.Folders.Item(folder_name)
        
        print(f"✅ 找到資料夾: {folder.Name} ({folder.Items.Count} 封郵件)")
        return folder
        
    except Exception as e:
        print(f"❌ 無法存取資料夾 {folder_name}: {e}")
        return None

def extract_emails_with_stats():
    """提取郵件並返回處理統計"""
    # Connect to Outlook
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    
    # Get the inbox folder - use the configured account and folder
    inbox = get_outlook_folder(outlook, ACCOUNT_NAME, FOLDER_NAME)
    
    # Connect to SQLite database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get messages sorted by received time (newest first)
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # True for descending (newest first)
    
    print(f"Found {len(messages)} items in '{inbox.Name}'. Processing...")
    print(f"📊 將處理最近 {MAX_EMAILS} 封郵件...")
    
    count = 0
    new_count = 0
    
    # Iterate through messages
    for msg in messages:
        if count >= MAX_EMAILS:
            print(f"✅ 已達到限制 {MAX_EMAILS} 封郵件")
            break
            
        try:
            # Check if it is a MailItem (Class 43)
            if msg.Class == 43:
                entry_id = msg.EntryID
                
                # Safe attribute access with defaults
                subject = getattr(msg, 'Subject', '(無主旨)')
                sender_name = getattr(msg, 'SenderName', 'Unknown')
                
                try:
                    sender_email = msg.SenderEmailAddress
                except:
                    sender_email = "Unknown"
                
                # Convert datetime to string for storage
                try:
                    received_time = str(msg.ReceivedTime)
                except:
                    received_time = str(datetime.datetime.now())
                
                # Safe body access
                try:
                    body = msg.Body if msg.Body else ""
                except:
                    body = "(無法讀取郵件內容)"
                
                # Apply body limit if specified
                if hasattr(globals(), 'BODY_LIMIT') and globals().get('BODY_LIMIT'):
                    try:
                        body_limit = int(globals()['BODY_LIMIT'])
                        if body_limit > 0:
                            body = body[:body_limit]
                    except:
                        pass  # 如果轉換失敗，保持原始 body
                
                # Check if exists and insert
                try:
                    c.execute("SELECT 1 FROM emails WHERE entry_id = ?", (entry_id,))
                    if c.fetchone() is None:
                        c.execute('''
                            INSERT INTO emails (entry_id, subject, sender_name, sender_email, received_time, body, folder)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (entry_id, subject, sender_name, sender_email, received_time, body, inbox.Name))
                        new_count += 1
                except Exception as db_error:
                    print(f"Database error processing email {entry_id}: {db_error}")
                    continue
                    new_count += 1
                
                count += 1
                if count % 50 == 0:
                    print(f"Processed {count} emails...")
                    conn.commit()
                    
        except Exception as e:
            print(f"Error processing a message: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"Done. Processed {count} emails. Added {new_count} new emails to {DB_NAME}.")
    print(f"Database location: {os.path.abspath(DB_NAME)}")
    
    return count, new_count

def extract_emails():
    """Connect to Outlook, extract emails, and save them to the database."""
    print("Connecting to Outlook...")
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        print(f"Failed to connect to Outlook. Make sure Outlook is installed and running. Error: {e}")
        return

    # 使用正確的帳號和資料夾
    inbox = get_outlook_folder(outlook, ACCOUNT_NAME, FOLDER_NAME)
    if not inbox:
        print(f"Failed to access folder '{FOLDER_NAME}' in account '{ACCOUNT_NAME}'")
        return
    
    # Optional: Select a specific subfolder if needed
    # inbox = inbox.Folders['SubfolderName'] 
    
    messages = inbox.Items
    # Sort by ReceivedTime descending to get newest first
    messages.Sort("[ReceivedTime]", True)

    conn = init_db()
    c = conn.cursor()

    print(f"Found {len(messages)} items in '{inbox.Name}'. Processing...")
    print(f"📊 將處理最近 {MAX_EMAILS} 封郵件...")
    
    count = 0
    new_count = 0
    
    # Iterate through messages
    for msg in messages:
        if count >= MAX_EMAILS:
            print(f"✅ 已達到限制 {MAX_EMAILS} 封郵件")
            break
            
        try:
            # Check if it is a MailItem (Class 43)
            if msg.Class == 43:
                entry_id = msg.EntryID
                subject = msg.Subject
                sender_name = msg.SenderName
                try:
                    sender_email = msg.SenderEmailAddress
                except:
                    sender_email = "Unknown"
                
                # Convert datetime to string for storage
                received_time = str(msg.ReceivedTime)
                body = msg.Body if msg.Body else ""
                
                # Check if exists
                c.execute("SELECT 1 FROM emails WHERE entry_id = ?", (entry_id,))
                if c.fetchone() is None:
                    c.execute('''
                        INSERT INTO emails (entry_id, subject, sender_name, sender_email, received_time, body, folder)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (entry_id, subject, sender_name, sender_email, received_time, body, inbox.Name))
                    new_count += 1
                
                count += 1
                if count % 50 == 0:
                    print(f"Processed {count} emails...")
                    conn.commit()
                    
        except Exception as e:
            print(f"Error processing a message: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"Done. Processed {count} emails. Added {new_count} new emails to {DB_NAME}.")
    print(f"Database location: {os.path.abspath(DB_NAME)}")

if __name__ == "__main__":
    extract_emails()
