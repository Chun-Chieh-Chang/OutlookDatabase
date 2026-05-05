#!/usr/bin/env python3
"""
Wiki Builder v2 — Small Batch Validation Test
Runs the new prompt on 3 emails and prints the raw LLM output for A/B comparison.
Does NOT write to wiki — this is a dry-run diagnostic.
Includes 15s delay between API calls to avoid Gemini 429 rate limiting.
"""

import os
import json
import glob
import sys
import io
import time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from email_analyzer import EmailAnalyzer

RAW_DIR = 'raw/emails'
TEST_LIMIT = 3

def run_test():
    print("=" * 60)
    print("  Wiki Builder v2 — Prompt Validation Test (Dry Run)")
    print("=" * 60)
    
    analyzer = EmailAnalyzer()
    
    if not analyzer.check_ollama_connection():
        print("❌ AI service not available.")
        return
    
    print(f"✅ AI Provider: {analyzer.provider} ({analyzer.model})")
    
    # Pick 3 diverse emails from different positions for variety
    email_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.json")))
    
    indices = [0, len(email_files)//2, len(email_files)-1]
    test_emails = []
    for i in indices[:TEST_LIMIT]:
        with open(email_files[i], 'r', encoding='utf-8') as f:
            test_emails.append((email_files[i], json.load(f)))
    
    results = []
    
    for idx, (filepath, data) in enumerate(test_emails, 1):
        print(f"\n{'─'*60}")
        print(f"📧 [{idx}/{TEST_LIMIT}] Subject: {data['subject']}")
        print(f"   Sender: {data.get('sender_name', 'N/A')}")
        print(f"   File: {os.path.basename(filepath)}")
        print(f"{'─'*60}")
        
        # Rate limit protection: wait between API calls
        if idx > 1:
            print(f"   ⏳ Waiting 15s to avoid Gemini rate limit...")
            time.sleep(15)
        
        analysis = analyzer.extract_wiki_entities(data['subject'], data['body'])
        
        dims = analysis.get('dimensions', [])
        print(f"\n   📊 Entities Extracted: {len(dims)}")
        
        # Score tracking
        email_score = {"has_category": 0, "no_others": 0, "has_desc": 0, 
                       "has_lifecycle": 0, "has_aliases": 0, "has_rels": 0, "total": len(dims)}
        
        for d in dims:
            cat = d.get('category', '?')
            name = d.get('name', '?')
            lc = d.get('lifecycle', 'none')
            imp = d.get('improvement', 'none')
            urg = d.get('urgency', '?')
            desc = d.get('description', '')[:80]
            aliases = d.get('aliases', [])
            rels = d.get('relationships', [])
            tags = d.get('tags', [])
            
            # Score
            if cat and cat != '?': email_score["has_category"] += 1
            if cat != 'others': email_score["no_others"] += 1
            if desc and '(Auto)' not in desc: email_score["has_desc"] += 1
            if lc in ['plan', 'do', 'check', 'act']: email_score["has_lifecycle"] += 1
            if aliases: email_score["has_aliases"] += 1
            if rels: email_score["has_rels"] += 1
            
            print(f"\n   ┌─ Entity: {name}")
            print(f"   │  Category:    {cat}")
            print(f"   │  Lifecycle:   {lc}")
            print(f"   │  Improvement: {imp}")
            print(f"   │  Urgency:     {urg}")
            print(f"   │  Tags:        {tags}")
            print(f"   │  Aliases:     {aliases}")
            print(f"   │  Description: {desc}...")
            if rels:
                print(f"   │  Relationships:")
                for r in rels:
                    print(f"   │    → {r.get('target', '?')} ({r.get('type', '?')})")
            print(f"   └─")
        
        # Calculate quality score for this email
        if email_score["total"] > 0:
            n = email_score["total"]
            quality = (
                email_score["has_category"] / n * 20 +
                email_score["no_others"] / n * 20 +
                email_score["has_desc"] / n * 20 +
                email_score["has_lifecycle"] / n * 20 +
                email_score["has_rels"] / n * 20
            )
            print(f"\n   📈 Quality Score: {quality:.0f}/100")
            email_score["quality"] = quality
        else:
            print(f"\n   ⚠️ No entities extracted!")
            email_score["quality"] = 0
        
        results.append(email_score)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    total_entities = sum(r["total"] for r in results)
    avg_quality = sum(r["quality"] for r in results) / len(results) if results else 0
    total_no_others = sum(r["no_others"] for r in results)
    total_has_lc = sum(r["has_lifecycle"] for r in results)
    total_has_rels = sum(r["has_rels"] for r in results)
    
    print(f"  Emails Tested:       {len(results)}")
    print(f"  Total Entities:      {total_entities}")
    print(f"  Avg Quality Score:   {avg_quality:.0f}/100")
    print(f"  Category ≠ Others:   {total_no_others}/{total_entities} ({total_no_others/total_entities*100:.0f}%)" if total_entities else "")
    print(f"  Has Lifecycle:       {total_has_lc}/{total_entities} ({total_has_lc/total_entities*100:.0f}%)" if total_entities else "")
    print(f"  Has Relationships:   {total_has_rels}/{total_entities} ({total_has_rels/total_entities*100:.0f}%)" if total_entities else "")
    
    # Pass/Fail
    if avg_quality >= 60:
        print(f"\n  ✅ PASS — Prompt v2 quality is acceptable. Proceed to wiki build.")
    else:
        print(f"\n  ❌ FAIL — Prompt needs further tuning before production run.")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    run_test()
