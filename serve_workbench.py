#!/usr/bin/env python3
"""Threaded HTTP server for the workbench — handles concurrent requests."""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

PORT = 8800
DIR = os.path.dirname(os.path.abspath(__file__))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

if __name__ == '__main__':
    os.chdir(DIR)
    server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Workbench server: http://localhost:{PORT}/work/")
    print(f"Serving from: {DIR}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
