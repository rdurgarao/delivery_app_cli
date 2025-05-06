import psycopg2
import qrcode
import os

DATABASE_NAME = 'delivery_app'


class PGDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(f"dbname={DATABASE_NAME} user=postgres port=5432 password=Gouse@1725")
        self.cur = self.conn.cursor()

    def execute(self, sql, vargs):
        self.cur.execute(sql, vargs)

    def get_latest_fetch(self):
        return self.cur.fetchone()[0]

    def commit_changes(self):
        self.conn.commit()

    def close_connections(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()


class ProductOrders:
    def create(self, product_id, order_id):
        self.product_id = product_id
        self.order_id = order_id
        db = PGDatabase()
        db.execute(
            "INSERT INTO products_orders (product_id, order_id) VALUES (%s, %s) RETURNING id;",
            (product_id, order_id))
        po_id = db.get_latest_fetch()
        db.close_connections()
        self.id = po_id


class Orders:
    def __init__(self, id, product_ids, status='created'):
        self.id = id
        self.product_ids = product_ids
        self.status = status

    @classmethod
    def find_by_id(cls, order_id):
        db = PGDatabase()
        db.execute("SELECT * from orders where id=%s", order_id)
        res = db.cur.fetchone()
        db.close_connections()
        new_order = Orders(0, [])
        new_order.id = res[0]
        new_order.total_price = res[1]
        new_order.status = res[2]
        return new_order

    @classmethod
    def validate_otp(cls, oid, otp):
        db = PGDatabase()
        db.execute("SELECT * from orders where id=%s and otp=%s", [oid[0], otp[0]])
        res = db.cur.fetchone()
        if res:
            db.execute("UPDATE orders set status='delivered' where id=%s", [oid[0]])
            db.close_connections()
            return True
        else:
            return False

    @classmethod
    def all_delivered_orders(cls):
        db = PGDatabase()
        db.execute("SELECT * FROM orders WHERE status='delivered'", [])
        res = db.cur.fetchall()
        db.close_connections()

        orders = []
        for row in res:
            order = Orders(id=row[0], product_ids=[], status=row[2])
            order.total_price = row[1]
            orders.append(order)
        return orders

    @classmethod
    def all_shipped_orders(cls):
        db = PGDatabase()
        db.execute("select * from orders where status='shipped'", [])
        res = db.cur.fetchall()
        db.close_connections()

        orders = []
        for row in res:
            order = Orders(id=row[0], product_ids=[], status=row[2])
            order.total_price = row[1]
            orders.append(order)
        return orders

    @classmethod
    def orders_created_details(cls):
        db = PGDatabase()
        db.execute("select * from orders where status='created'", [])
        res = db.cur.fetchall()
        db.close_connections()

        orders = []
        for row in res:
            order = Orders(id=row[0], product_ids=[], status=row[2])
            order.total_price = row[1]
            orders.append(order)
        return orders

    def update_order_shipment(self, otp):
        db = PGDatabase()
        db.execute("UPDATE orders set status='shipped', otp=%s where id=%s", [otp, self.id])
        db.close_connections()

    def create_qr(self, url):
        path = 'qrs'
        if not os.path.exists(path):
            os.makedirs('qrs')
        file_path = os.path.join(path, f'{self.id}.png')
        image = qrcode.make(url)
        image.save(file_path)
        return file_path

    def create(self):
        order_total_price = 0

        db = PGDatabase()
        db.execute(
            "INSERT INTO orders (total_price, status) VALUES (%s, %s) RETURNING id;",
            (order_total_price, 'created'))
        order_id = db.get_latest_fetch()
        self.id = order_id
        db.commit_changes()

        for pid in self.product_ids:
            product = Product.find(pid)
            order_total_price = order_total_price + product.price
            new_product_order = ProductOrders()
            new_product_order.create(product.id, self.id)

        db.execute("UPDATE orders set total_price=%s where id=%s", (order_total_price, self.id))
        db.close_connections()


class Product:
    def __init__(self, id, name, description, price, active=True, specs=None, type="Non Fr"):
        self.name = name
        self.description = description
        self.price = price
        self.active = active
        self.specs = specs
        self.type = type
        self.id = id

    def get_price(self):
        return "{:,.2f}".format(self.price)

    def __str__(self):
        return f"name - {self.name}, description - {self.description}, price - {self.price} "

    def __repr__(self):
        return self.__str__()

    def write_to_db(self):
        db = PGDatabase()
        db.execute(
            "INSERT INTO products (name, description, price, type, active) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (self.name[:10], self.description, self.price, self.type, self.active))
        product_id = db.get_latest_fetch()
        db.close_connections()
        self.id = product_id

    # def fetch_product_from_db(self):
    #     db = PGDatabase()
    #     db.execute("select * from products where id = %s;", (self.id,))
    #     res = db.cur.fetchall()
    #     print(res)
    #     db.close_connections()

    @classmethod
    def find(cls, id):
        db = PGDatabase()
        db.execute("select * from products where id = %s;", (id,))
        res = db.cur.fetchone()
        name = res[0]
        id = res[1]
        description = res[2]
        price = res[3]
        type = res[4]
        active = res[5]
        new_product = Product(id, name, description, price, type, active)
        db.close_connections()
        return new_product
