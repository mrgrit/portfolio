#!/usr/bin/env python3
"""포트폴리오 정적 서버 — site/ 만 127.0.0.1 로 내보낸다 (Cloudflare Tunnel 뒤).

    ./serve.py            # 127.0.0.1:4000
    ./serve.py 4100       # 포트 지정
"""
import http.server
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")


class Handler(http.server.SimpleHTTPRequestHandler):
    # 파이썬 3.10 의 mimetypes 는 webp 를 모른다
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".webp": "image/webp",
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        # assets 는 build.py 가 ?v=<해시> 를 붙이므로 길게 캐시해도 된다
        if self.path.startswith("/assets/"):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404)
        return None


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"portfolio: http://127.0.0.1:{port}/  (root={ROOT})", flush=True)
        httpd.serve_forever()
