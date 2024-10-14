import os
from http.server import HTTPServer, SimpleHTTPRequestHandler


class LocalHandler(SimpleHTTPRequestHandler):
    directory = os.fspath("./output")


def run():
    server_address = ("127.0.0.1", 8000)
    httpd = HTTPServer(
        server_address=server_address,
        RequestHandlerClass=LocalHandler,
    )
    print("Server running at http://127.0.0.1:8000")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
