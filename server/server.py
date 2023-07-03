import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import redis

client = redis.Redis(host='localhost', port=6379)


# Define the handler for incoming HTTP requests
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)

        if self.path == '/getAll':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            print(client.keys('*'))
            self.wfile.write(str(client.keys('*')).encode('utf-8'))
        elif self.path.split('?')[0] == '/getIp':
            username = query_components.get('username', [''])[0]
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(client.get(username)).encode('utf-8'))
        else:
            # Send a 404 Not Found response
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length)

        form_data = parse_qs(body.decode())
        if self.path == '/init':
            username = form_data.get('username', [''])[0]
            ip = form_data.get('ip', [''])[0]
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            data = json.loads(body.decode())
            # print(data['username'])
            client.set(data['username'], data['ip'])
            self.wfile.write('Done'.encode('utf-8'))
        else:
            # Send a 404 Not Found response
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')


# Start the HTTP server
if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Starting server on http://{server_address[0]}:{server_address[1]}')
    httpd.serve_forever()
