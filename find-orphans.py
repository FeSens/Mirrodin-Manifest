#!/usr/bin/env python3
"""Find orphan notes in an Obsidian vault (files with no [[wikilinks]] to/from other files)."""

import re
from pathlib import Path

def find_orphans(vault_path: str = ".") -> list[str]:
    vault = Path(vault_path)
    md_files = {f.stem for f in vault.rglob("*.md")}

    outgoing = {f: set() for f in md_files}
    incoming = {f: set() for f in md_files}

    # Match [[link]] or [[link|alias]] or [[link#heading]]
    wikilink_pattern = re.compile(r'\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]')

    for md_file in vault.rglob("*.md"):
        file_stem = md_file.stem
        try:
            content = md_file.read_text(encoding='utf-8')
            for link in wikilink_pattern.findall(content):
                link = link.strip()
                if link in md_files and link != file_stem:
                    outgoing[file_stem].add(link)
                    incoming[link].add(file_stem)
        except Exception:
            pass

    orphans = sorted(f for f in md_files if not outgoing[f] and not incoming[f])
    return orphans

if __name__ == "__main__":
    orphans = find_orphans()
    print(f"Scanned: {len({f.stem for f in Path('.').rglob('*.md')})} markdown files")
    print(f"Found: {len(orphans)} orphan files (no connections)\n")

    if orphans:
        print("Orphan files:")
        for o in orphans:
            print(f"- {o}.md")
    else:
        print("No orphans found - vault is fully connected!")
