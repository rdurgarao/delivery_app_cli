import http.server
import socketserver
import re
from urllib.parse import urlparse, parse_qs
from models import Orders
import random

BASE_URL = 'https://a0cc-223-185-48-233.ngrok-free.app/'

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        valid_ship_path = re.search("\/orders\/ship\?oid=\d+", self.path)
        valid_deliver_path = re.search("\/orders\/verify\?oid=\d+&otp=\d+", self.path)

        if valid_ship_path:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            oid = query_params['oid']

            order = Orders.find_by_id(oid)
            otp = str(random.randint(10000, 99999))

            if order and order.status == "created":
                order.update_order_shipment(otp)
                url = f'{BASE_URL}/orders/verify?oid={oid[0]}&otp={otp}'
                print(url)
                file_path = order.create_qr(url)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Not found")

            self.end_headers()
            # order_id = self.
        elif valid_deliver_path:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            oid = query_params['oid']
            otp = query_params['otp']

            order = Orders.find_by_id(oid)
            is_delivery_marked = Orders.validate_otp(oid, otp)

            if order.status == 'delivered' and is_delivery_marked:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Order delivered successfully !!")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Not found")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

PORT = 8000

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()