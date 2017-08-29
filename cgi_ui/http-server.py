import http.server
import socketserver

PORT = 8000

Handler = http.server.CGIHTTPRequestHandler

try:
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
except KeyboardInterrupt:
    print("End.")

"""
try:
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server('127.0.0.1', 8000, application)
    server.serve_forever()
    print("Webserver running...")
except KeyboardInterrupt:
    print("Webserver stopped...")
"""