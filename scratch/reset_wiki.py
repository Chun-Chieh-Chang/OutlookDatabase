import os
import shutil

def reset_wiki_state():
    wiki_dir = 'wiki'
    files_to_remove = [
        '.processed_emails.txt',
        '.alias_registry.json',
        'graph_store.json'
    ]
    
    print("--- Resetting Wiki State ---")
    for f in files_to_remove:
        path = os.path.join(wiki_dir, f)
        if os.path.exists(path):
            os.remove(path)
            print(f"Removed state file: {f}")

    # Delete all subdirectories in wiki/ except 'raw' (if any)
    # Actually, wiki_builder creates specific dirs. I will delete them to start fresh.
    target_subs = [
        'dimensions', 'lifecycle', 'improvement', 'projects', 
        'organizations', 'artifacts', 'domains', 'entities', 'concepts'
    ]
    
    for sub in target_subs:
        path = os.path.join(wiki_dir, sub)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"Cleared directory: {sub}")

    # Root files like index.md, nudge_list.md
    root_mds = ['index.md', 'nudge_list.md', 'Document_Collection_Request.md']
    for f in root_mds:
        path = os.path.join(wiki_dir, f)
        if os.path.exists(path):
            os.remove(path)
            print(f"Removed root page: {f}")

if __name__ == "__main__":
    reset_wiki_state()
    print("Wiki state reset complete. Ready for rebuild.")
