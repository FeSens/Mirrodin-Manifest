---
name: duplicate-text
description: Find cards with identical or similar rules text in the set. Use to identify duplicate abilities or cards that need differentiation.
allowed-tools: Bash(python3 *)
---

Run the duplicate text finder:

```bash
python3 duplicate-text.py
```

This will scan all cards and find those with identical OR similar rules text:

**What it checks:**
- Exact match of rules text between cards
- Fuzzy similarity matching (default 70% threshold)
- Groups exact duplicates, lists similar pairs

**Output:**
- Table of exact duplicates (identical text)
- Table of similar texts with similarity percentage
- Text comparison preview for each pair

Use this to identify:
- Cards that accidentally have the same ability
- Cards with too-similar effects that need differentiation
- Templated text that may need variation
- Potential copy-paste errors

Adjust `SIMILARITY_THRESHOLD` in the script (0.0-1.0) to find more/fewer matches.
