# Outlook to Database Implementation Plan

## Goal Description
The user wants to treat their local Outlook email data as a database to programmatically extract and use information. The solution will be a Python-based toolkit that:
1.  Connects to the local Outlook application using the Windows COM interface (`pywin32`).
2.  Extracts email metadata (Sender, Recipient, Subject, Body, Date) from specified folders (e.g., Inbox).
3.  Stores this data in a local SQLite database (`emails.db`).
4.  Provides a simple interface or examples to query this database using SQL or Python.

## User Review Required
> [!IMPORTANT]
> **Prerequisite:** This solution requires the classic **Outlook Desktop Application** (Windows) to be installed and configured. It works by automating the local Outlook client. It requires Python and the `pywin32` library.

## Proposed Changes

### Project Root
#### [NEW] [outlook_db_builder.py](outlook_db_builder.py)
A Python script that:
- Connects to Outlook via `win32com.client`.
- Iterates through the 'Inbox' (and potentially subfolders).
- Creates/Connects to a SQLite database.
- Upserts emails (prevents duplicates based on EntryID) into a table `emails`.

#### [NEW] [query_examples.py](query_examples.py)
A collection of Python functions showing how to:
- Connect to the `emails.db`.
- Run SQL queries (e.g., "Find all emails from X", "Find emails with extracting keyword Y").
- Show how an AI agent could use this structured data.

## Verification Plan

### Automated Tests
- I cannot automatedly test the connection to *your* specific Outlook instance from here.
- I will provide the code and you will need to run it locally.

### Manual Verification
- **Step 1**: User installs requirements: `pip install pywin32`
- **Step 2**: User runs `python outlook_db_builder.py`.
- **Step 3**: User verifies `emails.db` is created and populated.
- **Step 4**: User runs `python query_examples.py` to see data retrieval in action.
