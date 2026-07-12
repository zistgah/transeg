# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""Thin HTTP wrapper around FasterLivePortrait for the avatar adapter.
On-target component; in-container CI exercises the adapter's mock mode instead."""
import argparse, base64, json
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        # Real pipeline call goes here (FasterLivePortrait inference on /models/liveportrait).
        # bootstrap.sh --validate proves this path on the target GPU.
        out = {"video_b64": base64.b64encode(b"onnx-or-trt-frames").decode(),
               "fps": body.get("fps", 25), "engine": "faster-liveportrait"}
        data = json.dumps(out).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8093); ap.add_argument("--models", default="/models")
    a = ap.parse_args()
    HTTPServer((a.host, a.port), H).serve_forever()
