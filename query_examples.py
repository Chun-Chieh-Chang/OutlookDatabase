import sqlite3
import pandas as pd
import os

# Configuration
DB_NAME = 'emails.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def search_emails_by_keyword(keyword, limit=10):
    """Search for emails containing a specific keyword in the subject or body."""
    conn = get_connection()
    query = """
        SELECT subject, sender_name, received_time, body
        FROM emails
        WHERE subject LIKE ? OR body LIKE ?
        ORDER BY received_time DESC
        LIMIT ?
    """
    params = (f'%{keyword}%', f'%{keyword}%', limit)
    
    # Using pandas for nice display
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    print(f"\n--- Search Results for '{keyword}' (showing {len(df)} results) ---")
    if df.empty:
        print("No emails found.")
    else:
        # Display first few columns for readability
        print(df[['received_time', 'sender_name', 'subject']].to_string(index=False))
    return df

def get_email_stats():
    """Get some basic statistics about the emails."""
    conn = get_connection()
    
    print("\n--- Email Statistics ---")
    
    # Count total emails
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM emails")
    total = cursor.fetchone()[0]
    print(f"Total Emails: {total}")
    
    # Top 5 senders
    print("\nTop 5 Senders:")
    query = """
        SELECT sender_name, COUNT(*) as count
        FROM emails
        GROUP BY sender_name
        ORDER BY count DESC
        LIMIT 5
    """
    df_senders = pd.read_sql_query(query, conn)
    print(df_senders.to_string(index=False))
    
    conn.close()

def export_to_csv(filename='email_export.csv'):
    """Export the entire database to a CSV file."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM emails", conn)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\nDatabase exported to {os.path.abspath(filename)}")
    print(f"Exported {len(df)} emails")
    conn.close()

if __name__ == "__main__":
    print("Email Query Tool")
    print("Ensure you have run outlook_db_builder.py first to populate the database.")
    
    # Example 1: Get generic stats
    try:
        get_email_stats()
    except Exception as e:
        print(f"Error reading database: {e}")
        print("Did you run outlook_db_builder.py?")
        exit()

    # Example 2: Interactive search
    while True:
        choice = input("\nEnter a keyword to search (or 'q' to quit, 'e' to export CSV): ")
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'e':
            export_to_csv()
        else:
            search_emails_by_keyword(choice)
