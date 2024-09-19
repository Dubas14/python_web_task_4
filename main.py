import urllib.parse
import mimetypes
import json
import logging
import socket
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from threading import Thread


BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
SOCKET_HOST = 'localhost'
SOCKET_PORT = 5000




class Task4Framework(BaseHTTPRequestHandler):
    
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message':
                self.send_html('message.html')
            case __:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', 404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data,(SOCKET_HOST,SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('location', '/message')
        self.end_headers()
    
    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())
            
    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())
            
            
def save_data(data):
        parse_data = urllib.parse.unquote_plus(data.decode())
        try:
            parse_dict = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
            
            current_time = str(datetime.now())
            
            try:
                with open('storage/data.json', 'r', encoding='utf-8') as file:
                    data_json = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data_json = {}  

            data_json[current_time] = parse_dict
            with open('storage/data.json', 'w', encoding='utf-8') as file:
                json.dump(data_json, file, ensure_ascii=False, indent=4)
        
        except ValueError as e:
            logging.error(e)
        except OSError as e:
            logging.error(e)
                    
def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info("Starting socket server")
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            save_data(msg)
    except KeyboardInterrupted:
        pass
    finally:
        server_socket.close()
        
    
def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, Task4Framework)
    logging.info("Starting http server")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT)).start()
    Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT)).start()
    logging.info("Server is running")
