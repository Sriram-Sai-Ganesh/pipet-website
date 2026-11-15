#!/usr/bin/env python3
"""Build an anonymized copy of the site into dist-anon/.

In index.html, identifying content is wrapped as

    <!-- ANON:START -->
    ...shown on the public site...
    <!-- ANON:REPLACE
    ...shown on the anonymous site...
    ANON:END -->

Only index.html and the local files it references are copied (an allowlist),
so stray files such as paper_tex/ or unused logos never reach the output.
The build fails if any identifying string survives.

Local pages shown in an iframe are written into the iframe's srcdoc attribute.
anonymous.4open.science serves every page in a sandbox that takes away its origin,
and only lets its pages appear in an iframe on a page from its own origin, so an
iframe src would stay blank there.

Usage: ANON_CODE_URL=https://anonymous.4open.science/r/... python3 scripts/build_anon.py
Without ANON_CODE_URL the Code button is dropped from the anonymous page.
"""

import html as html_lib
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist-anon"

LEAK_PATTERNS = [
    r"Sriram",
    r"Sai Ganesh",
    r"ssaigan",
    r"Eisner",
    r"Tom Wang",
    r"Wang, Tom",
    r"\bjhu\b",
    r"Hopkins",
    r"argolab",
    r"sriram\.io",
    r"ANON:",
    r"__ANON_CODE_URL__",
]

ANON_BLOCK = re.compile(
    r"<!-- ANON:START -->.*?<!-- ANON:REPLACE(.*?)ANON:END -->", re.DOTALL
)
LOCAL_REF = re.compile(r'(?:src|href|content)="((?:static|\./static)/[^"#?]+)"')
IFRAME_SRC = re.compile(r'(<iframe\b[^>]*?\s)src="((?:static|\./static)/[^"#?]+\.html)"')


def anonymize(html):
    html = ANON_BLOCK.sub(lambda m: m.group(1), html)
    code_url = os.environ.get("ANON_CODE_URL")
    if code_url:
        html = html.replace("__ANON_CODE_URL__", code_url)
    else:
        print("warning: ANON_CODE_URL not set; dropping Code button", file=sys.stderr)
        html = re.sub(
            r'\s*<span class="link-block" data-anon-code>.*?</span>\s*</a>\s*</span>',
            "",
            html,
            flags=re.DOTALL,
        )
    # Drop remaining comments (TODOs etc.) so nothing identifying hides in them.
    return re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)


def inline_iframes(html):
    """Replace each local iframe src with a srcdoc holding that page's HTML."""

    def inline(m):
        page = (ROOT / os.path.normpath(m.group(2))).read_text()
        return f'{m.group(1)}srcdoc="{html_lib.escape(page)}"'

    return IFRAME_SRC.sub(inline, html)


def copy_with_refs(rel, seen):
    """Copy a local file, following references out of HTML files."""
    if rel in seen:
        return
    seen.add(rel)
    src = ROOT / rel
    if not src.is_file():
        sys.exit(f"error: referenced file missing: {rel}")
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix == ".html":
        text = src.read_text()
        if rel == "index.html":
            text = inline_iframes(anonymize(text))
        for ref in LOCAL_REF.findall(text):
            copy_with_refs(os.path.normpath(ref), seen)
        dst.write_text(text)
    else:
        shutil.copy2(src, dst)


def check_leaks():
    leaks = []
    for path in OUT.rglob("*"):
        if path.suffix not in {".html", ".css", ".js", ".json", ".txt", ".md", ".svg"}:
            continue
        text = path.read_text(errors="ignore")
        for pat in LEAK_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                line = text.count("\n", 0, m.start()) + 1
                leaks.append(f"{path.relative_to(OUT)}:{line}: {m.group(0)!r}")
    return leaks


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    seen = set()
    copy_with_refs("index.html", seen)
    # Serve files as-is on GitHub Pages.
    (OUT / ".nojekyll").touch()

    leaks = check_leaks()
    if leaks:
        print("error: identifying strings found in build:", file=sys.stderr)
        print("\n".join(leaks), file=sys.stderr)
        sys.exit(1)
    print(f"built {len(seen)} files into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
