"""Shared static navigation, used by every report builder."""
import re

PAGES = [("index.html", "Raw evidence"), ("ui/index.html", "Chart studio"),
         ("variant/index.html", "Decision filter"),
         ("executive/index.html", "Executive briefing")]


def portal_html(content, prefix="", current="index.html"):
    links = "".join(f'<a href="{prefix}{path}"' + (' aria-current="page"' if path == current else '')
                    + f'>{label}</a>' for path, label in PAGES)
    nav = '<!-- PORTAL START --><nav class="benchmark-nav" aria-label="Benchmark portal">' + links + '</nav><!-- PORTAL END -->'
    content = re.sub(r'<!-- PORTAL START -->.*?<!-- PORTAL END -->', '', content, flags=re.S)
    content = re.sub(r'<link[^>]*data-benchmark-portal[^>]*>', '', content)
    content = content.replace('</head>', f'<link data-benchmark-portal rel="stylesheet" href="{prefix}portal.css"></head>')
    return re.sub(r'(<body[^>]*>)', lambda m: m[1] + nav, content, count=1)
