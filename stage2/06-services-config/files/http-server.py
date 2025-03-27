import os
import json
import threading
import getpass
from jinja2 import Environment, FileSystemLoader
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


from apiv1.scanner import Scanner
from apiv1.system import System



def load_file_contents(file_path):
    """Reads the contents of a file and returns it."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found"


class Handler(BaseHTTPRequestHandler):
    SYSTEM: System = System()
    SCANNER: Scanner = Scanner()
    API_PATH = '/apiv1/'
    STATIC_PATH = "/static/"
    FAT_MAPS_PATH = "/fat_map/"
    STATIC_DIR = Path(f".{STATIC_PATH}")
    FAT_MAPS_DIR = Path(f".{FAT_MAPS_PATH}")
    STATICS = [f.name for f in STATIC_DIR.iterdir() if f.is_file()]
    FAT_MAPS = [f.name for f in FAT_MAPS_DIR.iterdir() if f.is_file()]    
    PAGE_GETS = {
        '/':                {  'title': 'Home', 'file': 'index.html'},
        '/fat':             {  'title': 'FAT', 'file': 'fat.html'},
        '/about':           {  'title': 'About', 'file': 'about.html'},
        '/scanner':         {  'title': 'Scanner', 'file': 'scanner.html'},        
    }

    PAGE_POSTS = {
        '/settings':        {  'title': 'Settings', 'file': 'settings.html'},
    }
    API_POSTS = {
        'scanner_start': {"cmd": SCANNER.start_thread},
        'scanner_upload_fat': {"cmd": SCANNER.upload_custom_fat_file},
    }
    API_GETS = {
        'scanner_status': {"cmd": SCANNER.status},
        'scanner_stop': {"cmd": SCANNER.stop_thread},
        'scanner_clear': {"cmd": SCANNER.clear_scan},
        'scanner_download_live_file': {"cmd": SCANNER.download_live_file},
        'scanner_restore_full_fat': {"cmd": SCANNER.restore_full_fat},
        'scanner_restore_proto_fat': {"cmd": SCANNER.restore_proto_fat},
        'scanner_restore_custom_fat': {"cmd": SCANNER.restore_custom_fat},
        'scanner_download_full_fat': {"cmd": SCANNER.download_full_fat},
        'scanner_download_proto_fat': {"cmd": SCANNER.download_proto_fat},
        'system_one_second': {"cmd": SYSTEM.one_second},
        'system_one_minute': {"cmd": SYSTEM.one_minute},
    }

    ENV = Environment(loader=FileSystemLoader('templates'))
    ENV.globals['load_file'] = load_file_contents

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        

    def get_content_type(self, file_extension):
        """Return the appropriate Content-Type header based on file extension."""
        if file_extension == ".css":
            return "text/css"
        elif file_extension == ".js":
            return "application/javascript"
        elif file_extension == ".png":
            return "image/png"
        elif file_extension == ".jpg" or file_extension == ".jpeg":
            return "image/jpeg"
        else:
            return "application/octet-stream"


    def serve_static_file(self, file_path):
        """Serve static files (CSS, JavaScript, images) from the /static/ folder."""
        file_extension = os.path.splitext(file_path)[1]
        content_type = self.get_content_type(file_extension)
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            with open(file_path, "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "File Not Found")


    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        if self.path.startswith(Handler.API_PATH):
            self._render_api(path=self.path, post_data=post_data)
        else:
            page = Handler.PAGE_POSTS.get(self.path, None)
            if page:
                self._render_page(page=page)
            else:
                self.send_error(404, "Not Found")


    def do_GET(self):
        if self.path.startswith(Handler.STATIC_PATH):
            if self.path.replace(Handler.STATIC_PATH, '') in Handler.STATICS:
                path = self.path[1:] # Remove leading slash
                try:
                    self.serve_static_file(path)
                except Exception:
                    self.send_error(404, "Static Not Found")
            else:
                self.send_error(404, "Not Found")
        
        elif self.path.startswith(Handler.FAT_MAPS_PATH):
            if self.path.replace(Handler.FAT_MAPS_PATH, '') in Handler.FAT_MAPS:
                path = self.path[1:] # Remove leading slash
                try:
                    self.serve_static_file(path)
                except Exception:
                    self.send_error(404, "Fat Map Not Found")
            else:
                self.send_error(404, "Not Found")
        elif self.path.startswith(Handler.API_PATH):
            self._render_api(path=self.path)
        else:
            page = Handler.PAGE_GETS.get(self.path, None)
            if page is not None:
                self._render_page(page=page)
            else:
                self.send_error(404, "Not Found")
                

    def _render_api(self, path: str, post_data: bytes = None):
        path = path.replace(Handler.API_PATH, '')
        response = {"status_code": 404, "error": False, 'data': None}
        if post_data: # POST API Call
            try:
                args = json.loads(post_data.decode('utf-8'))
                request = Handler.API_POSTS.get(path)
                if request:
                    cmd = request.get('cmd')
                    if cmd:
                        response["status_code"] = 200
                        response["data"] = cmd(args=args)
            except json.JSONDecodeError:
                response["status_code"] = 500
                response["error"] = "Invalid JSON in post data"
        else: # GET API Call
            request = Handler.API_GETS.get(path)
            if request:
                cmd = request.get('cmd')
                if cmd:
                    response["status_code"] = 200
                    response["data"] = cmd()

        self.send_response(response.get("status_code"))
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))


    def _render_page(self, page: dict):
        title = page.get('title')
        file = page.get('file')
        self.render_template(
            "layout.html", {
                'file': f'templates/{file}',
                "title": title,
            }, 200)


    def render_template(self, template_name, context, status_code):
        """Render a Jinja2 template with a given context and status code."""
        try:
            template = Handler.ENV.get_template(template_name)
            rendered_content = template.render(context)
            self.send_response(status_code)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rendered_content.encode("utf-8"))
        except Exception as e:
            self.send_error(500, f"Error rendering template: {e}")


port = 8000
user = getpass.getuser()
port = 80 if 'root' == getpass.getuser() else 8003
server = HTTPServer(('0.0.0.0', port), Handler)
server.serve_forever()