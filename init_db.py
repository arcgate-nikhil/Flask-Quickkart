from app import db, app, User  # Ensure User is imported to trigger table creation

# Ensure the app context is available
with app.app_context():
    # Drop all existing tables (if they exist)
    db.drop_all()

    # Now create all the tables again
    db.create_all()

    # Run the create_admin function to add the admin user
    from app import create_admin  # Import the function after db creation
    create_admin()

    print("Database initialized and admin user created!")
