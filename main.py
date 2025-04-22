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

    def close_connections(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

class Product:
    def __init__(self, name, description, price, active=True, specs=None, type="Non Fr"):
        self.name = name
        self.description = description
        self.price = price
        self.active = active
        self.specs = specs
        self.type = type

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

    def fetch_product_from_db(self):
        db = PGDatabase()
        db.execute("select * from products where id = %s;", (self.id,))
        res = db.cur.fetchall()
        print(res)
        db.close_connections()

def generate_products(size=100):
    products = []
    for n in range(size):
        fake = Faker()
        random_price = round(random.uniform(10, 1000), 2)
        new_product = Product(fake.catch_phrase(), fake.text(), random_price)
        products.append(new_product)

    return products

products = generate_products(20)
for product in products:
    product.write_to_db()
    product.fetch_product_from_db()
