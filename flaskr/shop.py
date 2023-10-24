from flask import (
    Blueprint,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("shop", __name__)


@bp.route("/")
def index():
    db = get_db()
    products = db.execute(
        "SELECT id, name, image_path, description, price FROM products"
    ).fetchall()
    user = g.user
    return render_template("shop/index.html", products=products, user=user)


@bp.route("/api/products")
def get_products_api():
    db = get_db()
    products = db.execute(
        "SELECT id, name, description, price FROM products"
    ).fetchall()
    products_data = [
        {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
        }
        for product in products
    ]
    return jsonify(products_data)


@bp.route("/api/cart_items")
@login_required
def get_cart_items_api():
    db = get_db()
    user_id = g.user["id"]

    # Get the last cart id for the user
    latest_cart_id = db.execute(
        "SELECT id FROM carts WHERE customer_id = ? ORDER BY id DESC LIMIT 1",
        [user_id],
    ).fetchone()

    if latest_cart_id:
        cart_id = latest_cart_id["id"]
        cart_items = db.execute(
            """
            SELECT
                c.product_quantity,
                p.name AS product_name
            FROM cart_items AS c
            JOIN products AS p ON c.product_id = p.id
            WHERE c.cart_id = ?
            """,
            [cart_id],
        ).fetchall()

        cart_items_data = [
            {
                "product_name": item["product_name"],
                "product_quantity": item["product_quantity"],
            }
            for item in cart_items
        ]

        return jsonify(cart_items_data)

    return jsonify([])


@bp.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    print(data)
    product_name = data.get("product_name")
    product_quantity = data.get("product_quantity")
    if product_name and product_quantity:
        user_id = g.user["id"]
        db = get_db()
        print(product_name)

        cart_id = db.execute(
            "SELECT id FROM carts WHERE customer_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchone()
        print(user_id)
        print(cart_id)
        print(2)
        if cart_id:
            cart_id = cart_id["id"]
            product = db.execute(
                "SELECT id FROM products WHERE name = ?",
                (product_name,),
            ).fetchone()

            if product:
                product_id = product["id"]
                print(product_id)
                db.execute(
                    "INSERT INTO cart_items (cart_id, product_id, product_quantity)"
                    " VALUES (?, ?, ?)",
                    (cart_id, product_id, product_quantity),
                )
                db.commit()
                return jsonify({"message": "Product added to cart successfully"})
            else:
                return jsonify({"message": "Product not found"}), 404
    return jsonify({"message": "Error 400"}), 400


@bp.route("/update_cart", methods=("POST",))
@login_required
def update_cart():
    data = request.get_json()

    product_name = data.get("product_name")
    new_quantity = data.get("new_quantity")

    if product_name and new_quantity:
        db = get_db()
        user_id = g.user["id"]

        # Retrieve the customer_id from the carts table based on the cart_id
        cart_info = db.execute(
            """
                SELECT c.customer_id
                FROM cart_items AS ci
                    JOIN carts AS c ON ci.cart_id = c.id
                    JOIN products AS p ON ci.product_id = p.id
                WHERE c.customer_id = ?
                    AND p.name = ?
            """,
            (user_id, product_name),
        ).fetchone()

        if cart_info:
            customer_id = cart_info["customer_id"]

            # Now you can update the cart item quantity
            db.execute(
                """
                    UPDATE cart_items
                    SET product_quantity = ?
                    WHERE id IN (
                        SELECT ci.id
                        FROM cart_items AS ci
                            JOIN carts AS c ON ci.cart_id = c.id
                            JOIN products AS p ON ci.product_id = p.id
                        WHERE c.customer_id = ?
                            AND p.name = ?
                    )
                """,
                (new_quantity, customer_id, product_name),
            )
            db.commit()
            return jsonify({"message": "Cart updated successfully"})
        else:
            return (
                jsonify(
                    {"message": "Cart not found for the specified user and product"}
                ),
                404,
            )

    return jsonify({"message": "Failed to update cart"}), 400


@bp.route("/remove_cart_item", methods=("POST",))
@login_required
def remove_cart_item():
    data = request.get_json()

    product_name = data.get("product_name")

    if product_name:
        db = get_db()
        user_id = g.user["id"]

        # Get the cart_id of the user's latest cart
        cart_id = db.execute(
            "SELECT id FROM carts WHERE customer_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()

        if cart_id:
            cart_id = cart_id["id"]

            # Delete the cart item based on product_name and cart_id
            db.execute(
                "DELETE FROM cart_items WHERE cart_id = ? AND product_id IN (SELECT id FROM products WHERE name = ?)",
                (cart_id, product_name),
            )
            db.commit()
            return jsonify({"message": "Item removed from cart_items successfully"})


@bp.route("/cart", methods=("GET", "POST"))
@login_required
def cart():
    if g.user is not None:
        db = get_db()
        user_id = g.user["id"]
        latest_cart_id = db.execute(
            "SELECT id FROM carts WHERE customer_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()

        if latest_cart_id:
            cart_id = latest_cart_id["id"]
            cart_items = db.execute(
                """
                SELECT cart_items.product_id, cart_items.product_quantity
                FROM cart_items
                WHERE cart_id = ?
                """,
                (cart_id,),
            ).fetchall()

            cart_items_list = []

            for item in cart_items:
                product_id = item["product_id"]
                product_quantity = item["product_quantity"]

                # Retrieve product details (name, description, price) using product_id
                product_details = db.execute(
                    "SELECT name, description, price FROM products WHERE id = ?",
                    (product_id,),
                ).fetchone()

                if product_details:
                    cart_item = {
                        "product_id": product_id,
                        "product_name": product_details["name"],
                        "product_quantity": product_quantity,
                        "description": product_details["description"],
                        "price": product_details["price"],
                    }
                    cart_items_list.append(cart_item)
            products = db.execute(
                "SELECT id, name, description, price FROM products"
            ).fetchall()

            return render_template(
                "shop/cart.html", cartItems=cart_items_list, products=products
            )

    return render_template("shop/cart.html", cartItems=[], products=[])


@bp.route("/order", methods=["POST"])
@login_required
def order():
    db = get_db()
    user_id = g.user["id"]

    db.execute("INSERT INTO carts (customer_id) VALUES (?)", (user_id,))
    db.commit()

    flash("Checkout completed. Your new cart is ready.")
    return redirect(url_for("shop.cart"))
