from application import app, db
from application.models import *

# create the database schema or even just test db connection
with app.app_context():
    db.drop_all()
    db.create_all()

    # adding sample categories and items
    jeans_category = Categories(name="Jeans")
    skirts_category = Categories(name="Skirt")
    tshirts_category = Categories(name="T-shirt")
    dresses_category = Categories(name="Dress")
    sweaters_category = Categories(name="Sweater")

    db.session.add(jeans_category)
    db.session.add(skirts_category)
    db.session.add(tshirts_category)
    db.session.add(dresses_category)
    db.session.add(sweaters_category)

    jeans_item = Items(
        name="Blue Force",
        stock=10,
        category=jeans_category,
        price=9.99,
        filename="jeans_1.jpg",
    )

    jeans_item_2 = Items(
        name="Dark Force",
        stock=999,
        category=jeans_category,
        price=9.99,
        filename="jeans_2.jpg",
    )

    skirt_item = Items(
        name="Comfy White",
        stock=999,
        category=skirts_category,
        price=4.99,
        filename="skirt_1.jpg",
    )

    skirt_item_2 = Items(
        name="Formal Blue",
        stock=5,
        category=skirts_category,
        price=4.99,
        filename="skirt_2.jpg",
    )

    tshirt_item = Items(
        name="Pricess Top",
        stock=999,
        category=tshirts_category,
        price=14.99,
        filename="tshirt_1.jpg",
    )

    tshirt_item_2 = Items(
        name="Flower Garden",
        stock=999,
        category=tshirts_category,
        price=14.99,
        filename="tshirt_2.jpg",
    )

    dress_item = Items(
        name="Black Dragon",
        stock=999,
        category=dresses_category,
        price=29.99,
        filename="dress_1.jpg",
    )

    dress_item_2 = Items(
        name="White Princess",
        stock=780,
        category=dresses_category,
        price=29.99,
        filename="dress_2.jpg",
    )

    sweater_item = Items(
        name="Comfy Light Blue",
        stock=999,
        category=sweaters_category,
        price=19.99,
        filename="sweater_1.jpg",
    )

    sweater_item_2 = Items(
        name="Green Peace",
        stock=999,
        category=sweaters_category,
        price=19.99,
        filename="sweater_2.jpg",
    )

    db.session.add(jeans_item)
    db.session.add(skirt_item)
    db.session.add(tshirt_item)
    db.session.add(dress_item)
    db.session.add(sweater_item)

    # added more items
    db.session.add(jeans_item_2)
    db.session.add(skirt_item_2)
    db.session.add(tshirt_item_2)
    db.session.add(dress_item_2)
    db.session.add(sweater_item_2)

    db.session.commit()
