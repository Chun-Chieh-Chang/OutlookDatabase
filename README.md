# Outlook Database Tool Usage Guide

This toolkit allows you to extract emails from your local Outlook application into a SQLite database (`emails.db`) and then query them programmatically.

## Prerequisites

1.  **Windows OS** having **Classic Outlook Desktop App** installed and configured with an account.
2.  **Python** installed.
3.  **Required Libraries**:
    Open your terminal (PowerShell or Command Prompt) and install the necessary packages:
    ```bash
    pip install pywin32 pandas
    ```

## How to Use

### 1. Build the Database
Run the builder script to extract emails from your Outlook Inbox.

```bash
python outlook_db_builder.py
```

- This script connects to Outlook.
- It reads emails from your 'Inbox'.
- It creates (or updates) `emails.db`.
- **Note**: The first run might take some time if you have thousands of emails. I set a limit of 500 emails for the first run in the code (`MAX_EMAILS = 500`). You can increase this in the file if needed.

### 2. Query the Data
Run the query tool to analyze your emails.

```bash
python query_examples.py
```

- This script connects to `emails.db`.
- It shows basic statistics (Total emails, Top senders).
- It allows you to **search** by keyword.
- It allows you to **export** the database to a CSV file.

## Advanced Usage (AI Integration)

Now that your data is in `emails.db`, you can use it with AI tools.

**Example Prompt for an AI coding assistant:**
> "Write a Python script that connects to `emails.db` and finds all emails related to 'Project Alpha' sent in the last month, then summarizes their content."

The database schema is simple:
- `entry_id`: Unique ID from Outlook
- `subject`: Email subject
- `sender_name`: Name of the sender
- `sender_email`: Email address of the sender
- `received_time`: Time received
- `body`: The text content of the email
