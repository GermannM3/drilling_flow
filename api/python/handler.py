from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'status': 'ok',
            'message': 'DrillFlow API is running'
        }
        self.wfile.write(json.dumps(response).encode())
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            data = json.loads(post_data.decode())
            response = {
                'status': 'ok',
                'received_data': data
            }
        except json.JSONDecodeError:
            response = {
                'status': 'error',
                'message': 'Invalid JSON data'
            }
            
        self.wfile.write(json.dumps(response).encode())