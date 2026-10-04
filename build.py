#!/usr/bin/env python3
"""data/projects.json → site/index.html

    ./build.py

표준 라이브러리만 쓴다. 프로젝트를 고치려면 data/projects.json 을 고치고 다시 돌린다.
스크린샷은 site/assets/shots/ 에 16:10 으로 넣고 "shot" 에 파일 이름을 적는다.
"""
import datetime
import hashlib
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "site")
e = html.escape


def asset(path):
    """내용 해시를 붙인 경로. serve.py 가 /assets/ 를 immutable 로 캐시하기 때문이다."""
    with open(os.path.join(SITE, path), "rb") as f:
        v = hashlib.sha1(f.read()).hexdigest()[:8]
    return f"/{path}?v={v}"


def host(url):
    return re.sub(r"^https?://", "", url).rstrip("/")


def ext(url, inner, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{e(url)}" target="_blank" rel="noopener">{inner}</a>'


ARROW = '<span class="arrow" aria-hidden="true">↗</span>'


def chips(p):
    if not p.get("stack"):
        return ""
    return '<ul class="chips">' + "".join(f"<li>{e(s)}</li>" for s in p["stack"]) + "</ul>"


def actions(p):
    out = []
    live = p.get("live")
    if live:
        out.append(ext(live["url"], f'{e(live["label"])} {ARROW}', "btn primary"))
    for m in p.get("more", []):
        out.append(ext(m["url"], f'{e(m["label"])} {ARROW}', "btn"))
    if p.get("repo"):
        out.append(ext(p["repo"], f"GitHub {ARROW}", "btn"))
    else:
        out.append('<span class="private">비공개 저장소</span>')
    return '<div class="actions">' + "".join(out) + "</div>"


def badge(p):
    if p.get("live"):
        return '<span class="badge live">Live</span>'
    if p.get("badge"):
        return f'<span class="badge">{e(p["badge"])}</span>'
    return ""


def frame(p):
    link = (p.get("live") or {}).get("url") or p.get("repo")
    addr = p.get("addr") or (host(p["live"]["url"]) if p.get("live") else "")
    if p.get("shot"):
        img = (
            f'<img src="{asset("assets/shots/" + p["shot"])}" alt="{e(p["alt"])}" '
            'width="1280" height="800" loading="lazy" decoding="async">'
        )
        inner = ext(link, img, "shot") if link else f'<div class="shot">{img}</div>'
    else:
        b = p["blank"]
        inner = f'<div class="blank"><strong>{e(b["title"])}</strong><span>{e(b["sub"])}</span></div>'
    return (
        '<div class="frame"><div class="bar"><span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>'
        f'<span class="addr">{e(addr)}</span></div>{inner}</div>'
    )


def card(p):
    access = f'<p class="access">{e(p["access"])}</p>' if p.get("access") else ""
    return f"""<article class="card">
{frame(p)}
<div class="body">
<div class="head"><h3>{e(p["name"])}</h3>{badge(p)}</div>
<p class="tagline">{e(p["tagline"])}</p>
<p class="desc">{e(p["desc"])}</p>
{chips(p)}
<div class="foot">{access}{actions(p)}</div>
</div>
</article>"""


def row(p):
    return f"""<article class="row">
<div class="who"><h3>{e(p["name"])}</h3><p class="tagline">{e(p["tagline"])}</p></div>
<div class="what"><p class="desc">{e(p["desc"])}</p>{chips(p)}</div>
{actions(p)}
</article>"""


def section(s):
    out = [
        f'<section class="block" id="{e(s["id"])}"><div class="wrap">',
        f'<header><p class="kicker">{e(s["kicker"])}</p><h2>{e(s["title"])}</h2><p>{e(s["lead"])}</p></header>',
    ]
    if s.get("cards"):
        cols = "three" if s.get("cols") == 3 else "two"
        out.append(f'<div class="grid {cols}">' + "\n".join(card(p) for p in s["cards"]) + "</div>")
    if s.get("rows"):
        out.append('<div class="rows">' + "\n".join(row(p) for p in s["rows"]) + "</div>")
    out.append("</div></section>")
    return "\n".join(out)


def main():
    with open(os.path.join(HERE, "data", "projects.json"), encoding="utf-8") as f:
        data = json.load(f)
    site, sections = data["site"], data["sections"]
    today = datetime.date.today().isoformat()

    projects = [p for s in sections for p in s.get("cards", []) + s.get("rows", [])]
    live = [p for p in projects if p.get("live")]
    repos = {"/".join(p["repo"].split("/")[:5]) for p in projects if p.get("repo")}
    lectures = next(s for s in sections if s["id"] == "lectures")["cards"]

    def endpoint(p):
        url = p["live"]["url"]
        inner = (
            f'<span class="host">{e(host(url))}</span><span class="what">{e(p["name"])}</span>'
            '<span class="go" aria-hidden="true">↗</span>'
        )
        return f"<li>{ext(url, inner)}</li>"

    board = "".join(endpoint(p) for p in live)
    nav = "".join(f'<a href="#{e(s["id"])}">{e(s["nav"])}</a>' for s in sections)
    og = site["url"].rstrip("/") + asset("assets/og.jpg")

    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(site["title"])}</title>
<meta name="description" content="{e(site["description"])}">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#090d18">
<link rel="canonical" href="{e(site["url"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(site["url"])}">
<meta property="og:title" content="{e(site["title"])}">
<meta property="og:description" content="{e(site["description"])}">
<meta property="og:image" content="{e(og)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="{asset("assets/style.css")}">
</head>
<body>
<a class="skip" href="#live">본문으로 건너뛰기</a>
<header class="top"><div class="wrap">
<a class="mark" href="/">dawnofagi<i>.cloud</i></a>
<nav aria-label="섹션">{nav}{ext(site["github"], f"GitHub {ARROW}", "gh")}</nav>
</div></header>

<main>
<section class="hero"><div class="wrap">
<div>
<p class="eyebrow">Dawn of AGI · Portfolio</p>
<h1>{e(site["name"])}</h1>
<p class="role"><b>{e(site["aka"])}</b> · {e(site["role"])}</p>
<p class="lead">{e(site["lead"].format(n=len(live)))}</p>
<blockquote class="motto">“{e(site["motto"])}”<cite>— {e(site["motto_from"])}</cite></blockquote>
<div class="cta"><a class="btn primary" href="#live">가동 중인 시스템 보기</a>{ext(site["github"], f"GitHub {ARROW}", "btn")}</div>
<dl class="stats">
<div><dt>바로 열리는 사이트</dt><dd>{len(live)}</dd></div>
<div><dt>공개 저장소</dt><dd>{len(repos)}</dd></div>
<div><dt>한국어 강좌</dt><dd>{len(lectures)}</dd></div>
</dl>
</div>
<aside class="board" aria-label="공개 엔드포인트">
<header><span>공개 엔드포인트</span><span><b>{len(live)}</b> · {today} 확인</span></header>
<ul>{board}</ul>
</aside>
</div></section>

{chr(10).join(section(s) for s in sections)}
</main>

<footer class="end"><div class="wrap">
<div><p>© {today[:4]} {e(site["name"])} ({e(site["aka"])}) · {e(site["role"])}</p>
<p class="fine">마지막 갱신 {today} · 이 페이지도 같은 서버에서 Cloudflare Tunnel로 서빙됩니다.</p></div>
<p>{ext(site["github"], e(host(site["github"])))}</p>
</div></footer>
</body>
</html>
"""
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print(f"site/index.html — 프로젝트 {len(projects)}개, 사이트 {len(live)}곳, 저장소 {len(repos)}개")


if __name__ == "__main__":
    main()
