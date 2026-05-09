import os

def rename_unknown_files(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            if 'Unknown' in f:
                old_path = os.path.join(root, f)
                # Remove 'Unknown' or replace with category name
                new_name = f.replace('_Unknown', '').replace('Unknown_', '').replace('Unknown', '未具名')
                new_path = os.path.join(root, new_name)
                
                try:
                    # If target exists, just remove the old one (keep the better named one)
                    if os.path.exists(new_path):
                        os.remove(old_path)
                    else:
                        os.rename(old_path, new_path)
                    count += 1
                except Exception as e:
                    print(f"Error renaming {f}: {e}")
                    
    print(f"Renamed/Cleaned {count} Wiki filenames.")

if __name__ == "__main__":
    rename_unknown_files('wiki')
