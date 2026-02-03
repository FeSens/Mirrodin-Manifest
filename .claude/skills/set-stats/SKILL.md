---
name: set-stats
description: Comprehensive MTG set statistics and dashboard generation. Use when analyzing the full set, generating reports, or updating the dashboard.
allowed-tools: Bash(python3 *)
---

Run the dashboard generator script and display full results:

```bash
python3 generate-dashboard.py
```

This will:
- Analyze all card markdown files in the vault
- Print full set summary to terminal (total cards, creatures, avg CMC)
- Show health metrics scored against set-guidelines.md
- List issues, warnings, and suggestions
- Regenerate `dashboard.html` with interactive charts

After running, offer to open the dashboard in the browser with `open dashboard.html`.
