from http.server import BaseHTTPRequestHandler, HTTPServer

def run_healthcheck_server():
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)
                self.end_headers()
        def log_message(self, format, *args):
            return  # Suppress logging
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    server.serve_forever() 