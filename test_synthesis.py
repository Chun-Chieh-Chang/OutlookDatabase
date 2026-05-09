import os
import json
from email_analyzer import EmailAnalyzer

def test_synthesis():
    analyzer = EmailAnalyzer()
    
    existing_content = """---
title: "Filter Base Project"
type: project
lifecycle: do
---

# Filter Base Project

## Description
Production of plastic filter bases for ICU Medical.

## Status
Current in T2 mold trial stage.
"""

    new_evidence = "The T3 trial was successful yesterday. We are moving to OQ validation next week."
    source_email = "[Re: Filter Base T3 Result](entry_id_123)"

    prompt = f"""You are a Knowledge Librarian. Your task is to SYNTHESIZE existing knowledge with new evidence into a cohesive Markdown Wiki page.

═══ EXISTING CONTENT ═══
{existing_content}

═══ NEW EVIDENCE ═══
Source: {source_email}
Content: {new_evidence}

═══ INSTRUCTIONS ═══
1. Integrate the new evidence into the existing content.
2. DO NOT just append. Rewrite the "Description" or "Status" sections if necessary.
3. Maintain the YAML frontmatter. Update the `updated` date to today.
4. Keep the output as a single valid Markdown file.
5. If there are specific records, list them under a "## Records" or "## History" section.

Output ONLY the updated Markdown.
"""

    print("--- TESTING SYNTHESIS PROMPT ---")
    result = analyzer.call_ai(prompt, "You are a professional knowledge synthesizer.")
    print(result)

if __name__ == "__main__":
    test_synthesis()
