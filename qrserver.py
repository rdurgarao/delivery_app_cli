import http.server
import socketserver
import re
from urllib.parse import urlparse, parse_qs
from models import Orders
import random

BASE_URL = '  https://16b6-2409-40f0-1049-3476-1427-8c6a-2e9e-2ded.ngrok-free.app/'


class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        valid_ship_path = re.search("\/orders\/ship\?oid=\d+", self.path)
        valid_deliver_path = re.search("\/orders\/verify\?oid=\d+&otp=\d+", self.path)
        valid_all_delivered_path = re.search("\/orders\/delivered\/", self.path)
        valid_all_shipped_path = re.search("\/orders\/shipped\/", self.path)
        valid_all_created_path = re.search("\/orders\/created\/",self.path)

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

        elif valid_all_delivered_path:
            delivered_orders = Orders.all_delivered_orders()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            if delivered_orders:
                for order in delivered_orders:
                    self.wfile.write(
                        f"Order ID: {order.id}, Total Price: {order.total_price}, Status: {order.status}\n".encode())
            else:
                self.wfile.write(b"No delivered orders found.")

        elif valid_all_shipped_path:
            shipped_orders = Orders.all_shipped_orders()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            if shipped_orders:
                for order in shipped_orders:
                    self.wfile.write(
                        f"Order ID: {order.id}, Total Price: {order.total_price}, Status: {order.status}\n".encode())
            else:
                self.wfile.write(b"no shipped orders found")

        elif valid_all_created_path:
            all_created_orders = Orders.orders_created_details()
            self.send_response(200)
            self.send_header("Content-type","text/plain")
            self.end_headers()
            if all_created_orders:
                for order in all_created_orders:
                    self.wfile.write(
                        f"order_id :{order.id}, Total_price: {order.total_price}, status : {order.status}".encode())
            else:
                self.wfile.write(b"No orders created")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")





PORT = 8000

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
