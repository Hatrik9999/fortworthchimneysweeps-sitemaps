#!/usr/bin/env python3
import datetime, re, sys, pathlib

TODAY = datetime.date.today().isoformat()  # YYYY-MM-DD
ROOT = pathlib.Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "sitemap-main.xml",
    ROOT / "sitemap-locations.xml",
]

def normalize_whitespace(s: str) -> str:
    return re.sub(r">\s+<", "><", s.strip())

def update_urlset(xml_text: str) -> str:
    urls = re.findall(r"(<url>.*?</url>)", xml_text, flags=re.DOTALL)
    if not urls:
        return xml_text
    by_loc = {}
    for block in urls:
        loc_match = re.search(r"<loc>(.*?)</loc>", block)
        if not loc_match:
            continue
        loc = loc_match.group(1).strip()
        if re.search(r"<lastmod>.*?</lastmod>", block):
            block = re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{TODAY}</lastmod>", block)
        else:
            block = re.sub(r"(</loc>)", rf"\1<lastmod>{TODAY}</lastmod>", block, count=1)
        by_loc[loc] = normalize_whitespace(block)
    ordered = [by_loc[k] for k in sorted(by_loc.keys(), key=lambda s: s.lower())]
    urlset_match = re.search(r"(?s)^(.*?<urlset[^>]*>)(.*)(</urlset>\s*)$", xml_text)
    if not urlset_match:
        return xml_text
    head, _, tail = urlset_match.groups()
    body = "\n  " + "\n  ".join(ordered) + "\n"
    return f"{head}{body}{tail}"

def update_index(xml_text: str) -> str:
    if "<sitemapindex" not in xml_text:
        return xml_text
    return re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{TODAY}</lastmod>", xml_text)

def run():
    changed = False
    for f in FILES:
        if not f.exists():
            continue
        old = f.read_text(encoding="utf-8")
        new = update_urlset(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            changed = True
    idx = ROOT / "sitemap_index.xml"
    if idx.exists():
        old = idx.read_text(encoding="utf-8")
        new = update_index(old)
        if new != old:
            idx.write_text(new, encoding="utf-8")
            changed = True
    print("changed=" + str(changed).lower())

if __name__ == "__main__":
    run()
