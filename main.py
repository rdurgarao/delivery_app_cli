from faker import Faker
import random
import psycopg2

DATABASE_NAME = 'delivery_app'

class PGDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(f"dbname={DATABASE_NAME} user=postgres port=5435")
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
        db.execute("INSERT INTO products (name, description, price, type, active) VALUES (%s, %s, %s, %s, %s) RETURNING id;", (self.name[:10], self.description, self.price, self.type, self.active))
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

def generate_products(size=100):
    products = []
    for n in range(size):
        fake = Faker()
        random_price = round(random.uniform(10, 1000), 2)
        new_product = Product(None, fake.catch_phrase(), fake.text(), random_price)
        products.append(new_product)

    return products

products = generate_products(30)
for product in products:
    product.write_to_db()
    # product.fetch_product_from_db()

pids = [product.id for product in products]

for i in range(100):
    order_size = random.randint(1, int(len(pids) / 4))
    random.shuffle(pids)
    o = Orders(None, pids[0:order_size])
    o.create()

print("data generated successfully")