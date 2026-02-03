---
name: find-orphans
description: Find orphan notes in the Obsidian vault - markdown files with no wikilinks connecting them to other files.
allowed-tools: Bash(python3 *)
---

Run the orphan finder script:

```bash
python3 find-orphans.py
```

This will:
- Scan all `.md` files in the current directory recursively
- Extract `[[wikilinks]]` from each file
- Identify files with zero incoming AND zero outgoing links
- Report the list of orphan files

Use case: Clean up Obsidian vaults by finding disconnected notes that may need linking or removal.
