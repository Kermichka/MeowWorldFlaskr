DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS carts;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  image_path TEXT NOT NULL,
  description TEXT
);

CREATE TABLE carts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES users (id)
);

CREATE TABLE cart_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  product_quantity INTEGER NOT NULL,
  FOREIGN KEY (product_id) REFERENCES products (id)
  FOREIGN KEY (cart_id) REFERENCES carts (id)
  UNIQUE (cart_id, product_id)
);

INSERT INTO products (name, price, image_path, description)
VALUES ('MeowMix', 549, 'shop/images/MeowMix.jpeg', '');

INSERT INTO products (name, price, image_path, description)
VALUES ('Instinct', 399, 'shop/images/Instinct.jpeg', '');

INSERT INTO products (name, price, image_path, description)
VALUES ('9Lives', 749, 'shop/images/9Lives.jpeg', '');
