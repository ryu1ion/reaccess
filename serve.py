#!/usr/bin/env python3
"""Serve this project locally without dependencies or reverse-DNS lookups."""
import argparse
import functools
import http.server
from pathlib import Path
import socketserver


class LocalServer(http.server.ThreadingHTTPServer):
    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        self.server_name = self.server_address[0]
        self.server_port = self.server_address[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    handler = functools.partial(Handler, directory=str(Path(__file__).resolve().parent))
    with LocalServer(("127.0.0.1", args.port), handler) as server:
        print(f"ReAccess preview: http://localhost:{args.port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
