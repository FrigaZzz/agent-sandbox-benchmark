"""Check local publication-draft length and links; drafts are intentionally ignored."""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    tasks = ROOT / "tasks"
    post_name = "linked" + "in-post.md"
    post = (tasks / post_name).read_text()
    body = post.split("<!-- POST_START -->", 1)[1].split("<!-- POST_END -->", 1)[0].strip()
    assert len(body) <= 3000, f"Social post exceeds 3,000 characters: {len(body)}"
    links = 0
    for page in [tasks / post_name, tasks / "medium-article.md"]:
        for link in re.findall(r'\]\(([^\s)]+)\)', page.read_text()):
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            assert (page.parent / unquote(parsed.path)).exists(), f"Missing draft link: {link}"
            links += 1
    print(f"PASS: post {len(body)}/3000 characters; {links} local draft links resolve. Public URL slots still need destinations.")


if __name__ == "__main__":
    main()
