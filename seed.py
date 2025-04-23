from app import app, db, Product

with app.app_context():
    product1 = Product(name="Cool Sneakers", price=999)
    product2 = Product(name="Graphic T-shirt", price=499)

    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()

    print("Products added successfully!")
