# from flask import Flask, jsonify, render_template
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
Scss(app, static_dir='static', asset_dir='assets')

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# MySQL database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flaskuser02:FlaskApp2025!@localhost/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'arcgate_01'
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))  # store image filename


# Model for User(Admin)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(15), nullable=False)


#Create an admin user 
def create_admin():
    with app.app_context():
        if not User.query.filter_by(username="admin101").first():
            admin = User(
                username="admin101",
                password=generate_password_hash("admin101password"),
                first_name="Admin",
                last_name="User",
                email="admin101@example.com",
                dob=datetime(1990, 1, 1),  # Or any valid date
                phone="1234567890"
            )
            db.session.add(admin)
            db.session.commit()
    
create_admin()

#Flask-Login user loader
@login_manager.user_loader
def load_user (user_id):
    return User.query.get(int(user_id))

# Home page
@app.route("/")
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        dob = datetime.strptime(request.form["dob"], "%Y-%m-%d").date()
        phone = request.form["phone"]

        # Check if username or email already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or Email already exists.")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            email=email,
            dob=dob,
            phone=phone
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/admin/users")
@login_required
def view_users():
    if current_user.username != "admin101":
        flash("Access denied.")
        return redirect(url_for("index"))
    
    users = User.query.all()
    return render_template("view_users.html", users=users)

@app.route("/product")
@login_required
def view_product():
    if current_user.username != "admin101":
        flash("Access denied.")
        return redirect(url_for("index"))
    
    products = Product.query.all()
    return render_template("view_product.html", products=products)

@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if current_user.username != "admin101":
        flash("Access denied.")
        return redirect(url_for("index"))

    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.price = request.form["price"]
        product.description = request.form["description"]

        image_file = request.files["image"]
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            product.image = filename

        db.session.commit()
        flash("Product updated successfully.")
        return redirect(url_for("index"))

    return render_template("edit_product.html", product=product)

@app.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    if current_user.username != "admin101":
        flash("Access denied.")
        return redirect(url_for("index"))

    product = Product.query.get_or_404(product_id)
    
    # Optional: Delete image file from disk
    if product.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
        except FileNotFoundError:
            pass

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.")
    return redirect(url_for("index"))


@app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.username != "admin101":
        flash("Only admin can add products.")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        image_file = request.files["image"]

        # Handle image
        filename = "default.png"  # Default image
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

        new_product = Product(name=name, price=price, description=description, image=filename)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("add_product"))

    return render_template("add_product.html")

# # API to get products
# @app.route("/api/products")
# def get_products():
#     products = Product.query.all()
#     return jsonify([{"id": p.id, "name": p.name, "price": p.price} for p in products])

# Login route
@app.route("/login", methods =["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect (url_for("index"))
        
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        user = User.query.filter_by(id=current_user.id).first()

        if not check_password_hash(user.password, current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("change_password"))
        elif new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for("change_password"))
        else:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password updated successfully.")
            return redirect(url_for("index"))

    return render_template("change_password.html")



#logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
        create_admin()
    app.run(debug=True, port=5003)

