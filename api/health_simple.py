from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "ok",
            "bot_info": {
                "id": "7554540052",
                "username": "Drill_Flow_bot",
                "first_name": "DrillFlow"
            },
            "webhook_url": f"https://{os.getenv('BOT_WEBHOOK_DOMAIN', 'drilling-flow.vercel.app')}/webhook"
        }
        
        self.wfile.write(json.dumps(response_data).encode()) 