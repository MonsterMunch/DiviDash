from flask import Flask
from extensions import db
from routes import main

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
    
    db.init_app(app)

    with app.app_context():
        db.create_all()  # This will create tables if they don't exist already

    app.register_blueprint(main)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)