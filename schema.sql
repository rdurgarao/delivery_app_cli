
create database delivery_app;

\c delivery_app;

drop table products;

create table products(name varchar(50), id integer primary key, description text, price integer, type varchar(10), specs text, active boolean);

create sequence products_id_seq INCREMENT BY 1 MINVALUE 1 START WITH 1 OWNED BY products.id;

ALTER TABLE products ALTER COLUMN id SET DEFAULT nextval('products_id_seq');
ALTER TABLE products ALTER COLUMN id SET NOT NULL;

insert into products (name, description, price, type, active) VALUES ('Lenovo Laptop', 'laptop looking awesome look with affordiable price', 45000, 'fragile', true);

create table orders(id SERIAL primary key, total_price integer, status varchar(20));

insert into orders (total_price, status) VALUES (20000, 'created');

create table products_orders(id SERIAL primary key, order_id integer, product_id integer, constraint products_orders_order_id foreign key(order_id) references orders(id), constraint products_orders_product_id foreign key(product_id) references products(id));

ALTER TABLE orders ADD COLUMN otp integer;

--truncate orders cascade;
--truncate products cascade;
--truncate products_orders cascade;