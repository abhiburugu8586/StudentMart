from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import os
from werkzeug.utils import secure_filename
from db.db import *
from functools import wraps

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
# Ensure uploads path is a directory (Windows can sometimes create it as a file)
if os.path.exists(UPLOAD_FOLDER) and not os.path.isdir(UPLOAD_FOLDER):
    os.remove(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Required for CSRF + sessions 
app.secret_key = "your_secret_key"
csrf = CSRFProtect(app)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        if not is_user_admin(session["user_id"]):
            flash("Admins only.", "danger")
            return redirect(url_for("index"))

        return view(*args, **kwargs)
    return wrapped


# CSRF token available in all templates 
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

# Global variable for site name used in templates 
siteName = "StudentMart"
@app.context_processor
def inject_site_name():
    return dict(siteName=siteName)


# Pages

@app.route("/")
def index():
    query = request.args.get("q", "").strip()

    if query:
        products = search_products(query, limit=12)
    else:
        products = get_all_products(limit=12)

    return render_template("index.html", products=products)

@app.route("/about")
def about():
    return render_template("about.html", title="About")


# Auth (Register/Login/Logout)

@app.route("/register/", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        repassword = request.form["repassword"]

        error = None
        if not username:
            error = "Username is required!"
        elif not password or not repassword:
            error = "Password is required!"
        elif password != repassword:
            error = "Passwords do not match!"
        elif get_user_by_username(username):
            error = "Username already exists! Please choose a different one."

        if error is None:
            create_user(username, password)
            flash(category="success", message=f"Registration successful! Welcome {username}!")
            return redirect(url_for("login"))

        flash(category="danger", message=f"Registration failed: {error}")

    return render_template("register.html", title="Register")

@app.route("/login/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        error = None
        if not username:
            error = "Username is required!"
        elif not password:
            error = "Password is required!"

        if error is None:
            user = validate_login(username, password)
            if user is None:
                error = "Invalid username or password!"
            else:
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash(category="success", message=f"Login successful! Welcome back {user['username']}!")
                return redirect(url_for("index"))

        flash(category="danger", message=f"Login failed: {error}")

    return render_template("login.html", title="Log In")

@app.route("/logout/")
def logout():
    session.clear()
    flash(category="info", message="You have been logged out.")
    return redirect(url_for("index"))


# Products

@app.route("/products/")
def products():
    category_id = request.args.get("category", default=None, type=int)
    cats = get_all_categories()
    items = get_all_products(category_id=category_id)
    return render_template("products.html", title="Products", categories=cats, products=items, selected_category=category_id)

@app.route("/product/<int:id>/")
def product(id):
    item = get_product_by_id(id)
    if item is None:
        flash(category="warning", message="Product not found!")
        return redirect(url_for("products"))
    return render_template("product.html", title=item["name"], product=item)


# Product CRUD (Admin/User-owned)


@app.route("/product/create/", methods=("GET", "POST"))
def product_create():
    if session.get("user_id") is None:
        flash(category="warning", message="You must be logged in to add products.")
        return redirect(url_for("login"))

    cats = get_all_categories()

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", type=float)

        # -------- Image handling --------
        image_url = ""
        file = request.files.get("image_file")
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_url = f"/static/uploads/{filename}"
            else:
                flash(category="danger", message="Invalid image type.")
                return render_template(
                    "product_form.html",
                    title="Add Product",
                    categories=cats,
                    product=None
                )
        else:
            image_url = request.form.get("image_url", "").strip()
        # --------------------------------

        stock = request.form.get("stock", type=int) or 0
        category_id = request.form.get("category", type=int)

        if not name:
            flash(category="danger", message="Product name is required!")
            return render_template("product_form.html", title="Add Product", categories=cats, product=None)

        if price is None:
            flash(category="danger", message="Price is required!")
            return render_template("product_form.html", title="Add Product", categories=cats, product=None)

        create_product(
            session["user_id"],
            category_id,
            name,
            description,
            price,
            image_url,
            stock
        )

        flash(category="success", message="Product created successfully!")
        return redirect(url_for("products"))

    return render_template("product_form.html", title="Add Product", categories=cats, product=None)

@admin_required
def product_create():
    ...



@app.route("/product/update/<int:id>/", methods=("GET", "POST"))
def product_update(id):
    if session.get("user_id") is None:
        flash(category="warning", message="You must be logged in to update products.")
        return redirect(url_for("login"))

    item = get_product_by_id(id)
    if item is None:
        flash(category="warning", message="Product not found!")
        return redirect(url_for("products"))

    # Permission check 
    if item["user"] != session.get("user_id"):
        flash(category="danger", message="You do not have permission to edit this product.")
        return redirect(url_for("product", id=id))

    cats = get_all_categories()

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", type=float)

        # -------- Image handling (Update) --------
        image_url = item["image_url"] or ""
        file = request.files.get("image_file")
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_url = f"/static/uploads/{filename}"
            else:
                flash(category="danger", message="Invalid image type.")
                return redirect(url_for("product_update", id=id))
        else:
            # Optional fallback: allow manual URL override
            url_from_form = request.form.get("image_url", "").strip()
            if url_from_form:
                image_url = url_from_form
        # ----------------------------------------

        stock = request.form.get("stock", type=int) or 0
        category_id = request.form.get("category", type=int)

        if not name:
            flash(category="danger", message="Product name is required!")
            return redirect(url_for("product_update", id=id))

        if price is None:
            flash(category="danger", message="Price is required!")
            return redirect(url_for("product_update", id=id))

        update_product(id, category_id, name, description, price, image_url, stock)
        flash(category="success", message="Product updated successfully!")
        return redirect(url_for("product", id=id))

    return render_template("product_form.html", title="Update Product", categories=cats, product=item)

@admin_required
def product_update(id):
    ...



@app.route("/product/delete/<int:id>/", methods=("POST",))
def product_delete(id):
    if session.get("user_id") is None:
        flash(category="warning", message="You must be logged in to delete products.")
        return redirect(url_for("login"))

    item = get_product_by_id(id)
    if item is None:
        flash(category="warning", message="Product not found!")
        return redirect(url_for("products"))

    if item["user"] != session.get("user_id"):
        flash(category="danger", message="You do not have permission to delete this product.")
        return redirect(url_for("product", id=id))

    delete_product(id)
    flash(category="success", message="Product deleted successfully!")
    return redirect(url_for("products"))
@admin_required
def product_delete(id):
    ...


@app.route("/cart/")
def cart_view():
    if session.get("user_id") is None:
        flash("Please login to view your cart.", "warning")
        return redirect(url_for("login"))

    items = cart_get_items(session["user_id"])
    total = sum(row["price"] * row["quantity"] for row in items)
    return render_template("cart.html", title="Your Cart", cart_items=items, total=total)


@app.route("/cart/add/<int:product_id>/", methods=("POST",))
def cart_add(product_id):
    if session.get("user_id") is None:
        flash("Please login to add items to cart.", "warning")
        return redirect(url_for("login"))

    qty = request.form.get("qty", type=int) or 1
    cart_add_item(session["user_id"], product_id, qty)
    flash("Added to cart.", "success")
    return redirect(url_for("cart_view"))


@app.route("/cart/update/<int:product_id>/", methods=("POST",))
def cart_update(product_id):
    if session.get("user_id") is None:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    qty = request.form.get("qty", type=int) or 0
    cart_update_quantity(session["user_id"], product_id, qty)
    flash("Cart updated.", "info")
    return redirect(url_for("cart_view"))


@app.route("/checkout/", methods=("POST",))
def checkout():
    if session.get("user_id") is None:
        flash("Please login to checkout.", "warning")
        return redirect(url_for("login"))

    order_id = order_create_from_cart(session["user_id"])
    if order_id is None:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products"))

    flash(f"Order placed successfully! Order #{order_id}", "success")
    return redirect(url_for("order_receipt", order_id=order_id))


@app.route("/orders/")
def orders():
    if session.get("user_id") is None:
        flash("Please login to view orders.", "warning")
        return redirect(url_for("login"))

    my_orders = orders_for_user(session["user_id"])
    return render_template("orders.html", title="My Orders", orders=my_orders)


@app.route("/orders/<int:order_id>/")
def order_receipt(order_id):
    if session.get("user_id") is None:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    order = order_get(order_id)
    if order is None or order["user_id"] != session["user_id"]:
        flash("Order not found.", "danger")
        return redirect(url_for("orders"))

    items = order_get_items(order_id)
    return render_template("order_receipt.html", title=f"Order #{order_id}", order=order, items=items)

if __name__ == "__main__":
    app.run(debug=True)
