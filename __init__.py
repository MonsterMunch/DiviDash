from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
    
    db.init_app(app)

    with app.app_context():
        db.create_all()  # This will create tables if they don't exist already

    return app

app = create_app()

from .views import main  # Import routes after the app is created
app.register_blueprint(main)