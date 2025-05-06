from faker import Faker
import random
from models import Product, Orders


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
