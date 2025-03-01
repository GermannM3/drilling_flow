from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "python_version": sys.version,
            "environment": {
                "VERCEL_URL": os.getenv("VERCEL_URL"),
                "BOT_WEBHOOK_DOMAIN": os.getenv("BOT_WEBHOOK_DOMAIN"),
                "USE_POLLING": os.getenv("USE_POLLING"),
                "DEBUG": os.getenv("DEBUG")
            },
            "webhook_url": f"https://{os.getenv('BOT_WEBHOOK_DOMAIN', 'drilling-flow.vercel.app')}/webhook"
        }
        
        self.wfile.write(json.dumps(response_data).encode()) 