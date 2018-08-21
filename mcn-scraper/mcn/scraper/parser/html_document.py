import bs4


def parse(html):
    soup = bs4.BeautifulSoup(html, "lxml")
    doc = dict()
    parse_meta(soup, doc)
    parse_title(soup, doc)
    parse_scripts(soup, doc)
    parse_links(soup, doc)
    return doc


def parse_meta(soup, doc):
    if not soup.head:
        return
    tags = (soup.head.find_all(name="meta") or [])
    meta = {}
    for tag in tags:
        k = tag.get("name")
        if not k:
            k = tag.get("property")
        if k:
            v = tag.get("content")
            meta.update({k: v})
    doc.update(meta=meta)


def parse_title(soup, doc):
    if not soup.head:
        return
    title = soup.head.find(name="title")
    doc.update(title=(title.text.strip() if title else None))


def parse_scripts(soup, doc):
    tags = []

    if soup.head:
        tags.extend(soup.head.find_all(name="script"))

    if soup.body:
        tags.extend(soup.body.find_all(name="script"))

    scripts = []
    for tag in tags:
        script_type = tag.get("type")
        src = tag.get("src")
        script = dict()
        if script_type:
            script.update(type=script_type)
        if src:
            script.update(src=src)
        if not src and tag.text:
            script.update(text=tag.text.strip())
        scripts.append(script)
    doc.update(scripts=scripts)


def parse_links(soup, doc):
    tags = soup.body.find_all(name="a") if soup.body else []
    links = []
    for tag in tags:
        href = tag.get("href")
        if not href:
            continue
        link = dict(
            href=href,
            text=tag.text.strip()
        )
        name = tag.get("name")
        id = tag.get("id")
        if name:
            link.update(name=name)
        if id:
            link.update(id=id)

        links.append(link)
    doc.update(links=links)


if __name__ == "__main__":
    import sys

    for f in sys.argv[1:]:
        parse_html(open(f, "r").read())
