import sqlite3, re, os, json

def get_strike_targets():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT subject, body FROM emails')
    
    freq = {}
    p = re.compile(r'[RVX]\d{1,2}-\d{4,5}[A-Z]*')
    
    for subject, body in cursor:
        text = (subject or '') + ' ' + (body or '')
        matches = p.findall(text)
        for m in matches:
            freq[m] = freq.get(m, 0) + 1
            
    # Get top entities that don't have files yet
    top_all = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    targets = []
    for t, f in top_all:
        # Check in all dimensions
        exists = False
        for root, dirs, files in os.walk('wiki'):
            if f"{t.replace('/', '_')}.md" in files:
                exists = True
                break
        if not exists:
            targets.append(t)
        if len(targets) >= 50:
            break
    
    print(json.dumps(targets))

if __name__ == "__main__":
    get_strike_targets()
