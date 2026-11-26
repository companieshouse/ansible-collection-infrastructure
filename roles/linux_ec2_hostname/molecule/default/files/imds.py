import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


RESPONSE = Path("/run/ec2-hostname-test-response.json")
TOKEN = "ec2-hostname-test-token"


class MetadataHandler(BaseHTTPRequestHandler):
    def configuration(self):
        if RESPONSE.exists():
            return json.loads(RESPONSE.read_text())
        return {}

    def respond(self, status, body):
        payload = body.encode()
        self.send_response(status)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_PUT(self):
        if (
            self.path != "/latest/api/token"
            or self.headers.get("X-aws-ec2-metadata-token-ttl-seconds") != "60"
        ):
            self.respond(400, "Incorrect token path or TTL")
            return
        config = self.configuration()
        self.respond(config.get("token_status", 200), config.get("token", TOKEN))

    def do_GET(self):
        if self.headers.get("X-aws-ec2-metadata-token") != TOKEN:
            self.respond(401, "Correct IMDSv2 token required")
            return
        config = self.configuration()
        tag_key = config.get("tag_key", "Hostname")
        if self.path != f"/latest/meta-data/tags/instance/{tag_key}":
            self.respond(404, "Incorrect tag path")
            return
        if config.get("disconnect"):
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        self.respond(config.get("status", 200), config.get("body", "boot.example.internal"))


HTTPServer(("127.0.0.1", 18080), MetadataHandler).serve_forever()
