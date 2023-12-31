from application import app, db
from application.models import (
    Items,
    Categories,
    ShippingForm,
    Customers,
    PaymentForm,
    Orders,
    OrdersItems,
)
from flask import render_template, jsonify, redirect, url_for, request, session
import random


@app.route("/")
@app.route("/home")
def index():
    # a bit of trickery, we get random items
    total_items = Items.query.count()

    # number of items we want to retrieve
    # for now, it's pretty much the entire database
    n_items = 4

    # generating random indices for selecting random items
    random_indices = random.sample(range(1, total_items + 1), n_items)

    # we query the database for the items with the generated indices
    random_items = Items.query.filter(Items.item_id.in_(random_indices)).all()

    # rendering appropriate template
    return render_template("index.html", items=random_items)


@app.route("/products")
def products():
    # retrieving all items
    items = Items.query.all()
    # rendering appropriate template
    return render_template("items.html", items=items)


@app.route("/products/<int:item_id>")
def product_details(item_id: int):
    # retrieving item using passed item_id
    item = Items.query.filter_by(item_id=item_id).first()
    # rendering appropriate template
    return render_template("product_details.html", item=item)


@app.route("/categories")
def categories():
    categories = Categories.query.all()
    # adding an "all categories" option to the list of categories
    all_categories = [{"category_id": -1, "name": "All Categories"}] + categories
    return render_template("categories.html", categories=all_categories)


@app.route("/get_products_by_category/<int:category_id>")
def get_products_by_category(category_id):
    # retrieve items that are part of the selected category
    items = Items.query.filter_by(category_id=category_id).all()
    # create list with all items
    items_list = [
        {
            # further fields can be added if they need to be displayed (e.g., product description)
            "item_id": items.item_id,
            "name": items.name,
            "price": items.price,
            "filename": items.filename,
        }
        for items in items
    ]
    # return JSON data so we can use it in categoriesProducts.js
    # this is done in such a way as to not need a page reload
    # every time the user clicks on a different category
    return jsonify({"items": items_list})


@app.route("/get_all_items")
def get_all_items():
    # this function is just used to display the All Categories items in the categories page
    # might be useful for future things?
    # the all_items view function unfortunately can't be reused since it renders a particular templat
    items = Items.query.all()
    # create list with all items
    items_list = [
        {
            # further fields can be added if they need to be displayed (e.g., product description)
            "item_id": items.item_id,
            "name": items.name,
            "price": items.price,
            "filename": items.filename,
        }
        for items in items
    ]
    # return JSON data so we can use it in categoriesProducts.js
    return jsonify({"items": items_list})


###################################################################
# cart page routes


@app.route("/cart")
def cart_page():
    # retrieving cart from session
    cart = session.get("cart", {})

    total_price = calculate_total_cart_price(cart)

    return render_template("cart_page.html", cart=cart, total_price=total_price)


@app.route("/add_to_cart/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    # get item by id
    # the reason why we re-retrieve the item instead of just passing
    # all the necessary fields is
    # 1) simplified view function
    # 2) if item data changes WHILE the user is on the site (i.e., price)
    #    the change wouldn't be reflected in what the user is seeing
    item = Items.query.filter_by(item_id=item_id).first()

    # retrieve selected quantity
    quantity = int(request.form["quantity"])

    # check if there's already a cart in session
    if "cart" not in session:
        session["cart"] = {}

    # else create it
    cart = session["cart"]

    # we cast to strings to keep data serialisable
    # if item is already in the cart, we just need to increase the quantity
    if str(item_id) in cart:
        cart[str(item_id)]["quantity"] += quantity
    else:
        # creation of "item info" dict
        # contains data which will be useful to be displayed in the cart page
        cart[str(item_id)] = {
            "name": item.name,
            "filename": item.filename,
            "price": item.price,
            "category": item.category.name,
            "quantity": quantity,
            "stock": item.stock,
        }

    # indicating that the session has been modified
    session.modified = True

    # redirecting to cart page
    return redirect(url_for("cart_page"))


def calculate_total_cart_price(cart):
    # calculating total price
    total_price = 0

    for _, item_info in cart.items():
        total_price += item_info["price"] * item_info["quantity"]

    # it's fine for it to be a string since we just need to display it for now
    total_price = "%.2f" % total_price

    return total_price


@app.route("/remove_from_cart/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    # retrieving cart
    cart = session.get("cart", {})

    # extra security
    if str(item_id) in cart:
        cart.pop(str(item_id))
        session.modified = True

        return (
            jsonify(
                {
                    "message": "Item removed from the cart successfully",
                    "cart_length": len(cart),
                }
            ),
            200,
        )
    return jsonify({"message": "Item not found in the cart"}), 400


@app.route("/decrease_quantity/<int:item_id>", methods=["POST"])
def decrease_quantity(item_id):
    # retrieving cart
    cart = session.get("cart", {})

    # extra security
    if str(item_id) in cart:
        # we decrease the quantity only if it amounts to more than 1
        if cart[str(item_id)]["quantity"] > 1:
            cart[str(item_id)]["quantity"] -= 1
            session.modified = True

        # get the updated quantity
        updated_quantity = cart[str(item_id)]["quantity"]

        # calculating updated cart total price
        updated_total_price = calculate_total_cart_price(cart)

        return jsonify(
            {
                "message": "Item quantity decreased successfully",
                "updated_quantity": updated_quantity,
                "updated_total_price": updated_total_price,
            }
        )

    return jsonify({"message": "Item not found in the cart"}), 400


@app.route("/increase_quantity/<int:item_id>", methods=["POST"])
def increase_quantity(item_id):
    # retrieving cart
    cart = session.get("cart", {})

    # extra security
    if str(item_id) in cart:
        # we first check whether the specified quantity is less than the item stock level
        if cart[str(item_id)]["quantity"] < cart[str(item_id)]["stock"]:
            # increasing item quantity
            cart[str(item_id)]["quantity"] += 1
            session.modified = True

        # get the updated quantity
        updated_quantity = cart[str(item_id)]["quantity"]

        # calculating updated cart total price
        updated_total_price = calculate_total_cart_price(cart)

        return jsonify(
            {
                "message": "Item quantity increased successfully",
                "updated_quantity": updated_quantity,
                "updated_total_price": updated_total_price,
            }
        )
    return jsonify({"message": "Item not found in the cart"}), 400


###################################################################
# checkout


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    # user can go to checkout page only if there's at least one item in the cart

    # retrieving cart
    cart = session.get("cart", {})

    # if the cart is empty, redirect to the cart page
    if len(cart) < 1:
        return redirect(url_for("cart_page"))
    else:
        total_price = calculate_total_cart_price(cart)

        form = ShippingForm()

        if form.validate_on_submit() and request.method == "POST":
            # get data from the shipping form
            # we use session variables to store data temporarily across different views
            session["customer_data"] = {
                "name": form.name.data,
                "email": form.email.data,
                "address": form.address.data,
                "post_code": form.post_code.data,
                "country": form.country.data,
            }

            # check if the customer is already in the system
            existing_customer = Customers.query.filter_by(
                email=session["customer_data"]["email"]
            ).first()

            # here, we should give the option to login if the user hasn't done so already
            if existing_customer:
                # redirect(url_for("login"))
                pass
            else:
                # customer is not in the system, add them
                new_customer = Customers(
                    name=session["customer_data"]["name"],
                    email=session["customer_data"]["email"],
                )
                db.session.add(new_customer)
                db.session.commit()

            # redirect to payment page
            return redirect(url_for("payment"))

        return render_template(
            "checkout.html", cart=cart, total_price=total_price, shipping_form=form
        )


@app.route("/payment", methods=["GET", "POST"])
def payment():
    # retrieving cart
    cart = session.get("cart", {})

    # retrieving customer data
    customer_data = session.get("customer_data", {})

    # if there isn't any customer data, we redirect to checkout
    # this is not really needed but just in case someone tries to
    # directly go to the /payment endpoint, skipping the checkout
    if not customer_data:
        return redirect(url_for("checkout"))
    else:
        total_price = calculate_total_cart_price(cart)

        form = PaymentForm()

        if form.validate_on_submit() and request.method == "POST":
            # do stuff on submit

            cardholder_name = form.cardholder_name.data
            card_number = form.card_number.data
            expiry_date = form.expiry_date.data
            security_code = form.security_code.data

            # if this data were to be stored somewhere (i.e, customers table)
            # we'd definitely need to use some sort of encryption (i.e., bcrypt)
            # however, at this point it isn't stored anywhere so using encryption is redundant (?)

            # here, get external payment processor result
            payment_result = process_payment(
                cardholder_name, card_number, expiry_date, security_code
            )

            # for this mock processor, the payment will pretty much always be successful
            if payment_result == "success":
                # get the customer
                customer = Customers.query.filter_by(
                    email=customer_data["email"]
                ).first()

                # build entire shipping address
                # this has to be done like this for now due to the poor
                # modularity for the customer's shipping address
                # TODO: Refactor shipping information (starting from the db schema)
                # TODO: Add countries drop down
                # TODO: Add Find your address functionality based on post code
                shipping_address = f"{customer_data['address']}, {customer_data['post_code']}, {customer_data['country']}"

                # track the order
                order = Orders(customer=customer, shipping_address=shipping_address)

                # adding to db session - transient for now
                db.session.add(order)

                # we also track all the items in an order
                # get all the ids
                for item_id, item_info in cart.items():
                    # retrieve items straight from the db
                    # even though we have all the data available here
                    # it's better to get the most udpated data in case of sudden price changes (according to a future admin account)
                    item = Items.query.filter_by(item_id=item_id).first()

                    # create relationship between orders and items
                    orders_items = OrdersItems(
                        orders=order, items=item, quantity=item_info["quantity"]
                    )

                    # adding to db session - transient for now
                    db.session.add(orders_items)

                    # we also need to update the Items table (i.e., update stock)
                    # for each item in the cart
                    item.stock = item.stock - item_info["quantity"]

                # commit everything to db
                db.session.commit()

                # redirect to order processed (payment result and order recap - customer details and items ordered)
                return redirect(url_for("process_order"))
            else:
                # payment wasn't successful
                # TODO: Once a proper payment processor has been set up, complete this section
                pass

        return render_template(
            "payment.html", cart=cart, payment_form=form, total_price=total_price
        )


@app.route("/process_order")
def process_order():
    # retrieving cart
    cart = session.get("cart", {})

    # retrieving customer data
    customer_data = session.get("customer_data", {})

    # if customer tried to directly access this page
    # there are definitely better ways to do this but again, time constraint
    # TODO: Refactor
    if not customer_data:
        return redirect(url_for("checkout"))
    # TODO: Add redirect in case payment details have not been entered
    else:
        total_price = calculate_total_cart_price(cart)

        # this section is of utmost importance for obvious security reasons
        # the amount of session attacks is quite large
        # clear session variables
        session.pop("cart", None)
        session.pop("customer_data", None)

        return render_template(
            "process_order.html",
            cart=cart,
            customer_data=customer_data,
            total_price=total_price,
        )


def process_payment(cardholder_name, card_number, expiry_date, security_code):
    # here, we'd have to build an API request
    # be careful of all the external payment processor security guidelines (i.e., how to send data, etc)
    # the payment processor will return, based on its API, a success or declined response

    # for the sake of this project the result will always be successful

    # to get the total price that the customer should be charged, we have two options
    # 1) query the database tables and figure out the price based on a combination of order info and items info
    # 2) directly compute it here as total_price using the calculate_total_price (most likely choice)

    # -> Note: I'm not quite sure whether storing the total price for each order is a good idea
    #          due to the 3 normalisation "rules" of databases design

    return "success"
