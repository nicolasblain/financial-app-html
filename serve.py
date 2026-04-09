#!/usr/bin/env python3
"""Tiny dev server. Bound to this directory via an absolute path so it works
even when the parent shell's cwd is unreadable."""
import functools
import http.server
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"Serving {ROOT} on http://127.0.0.1:{PORT}", flush=True)
    httpd.serve_forever()
