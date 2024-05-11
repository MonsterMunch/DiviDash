from flask import Flask, render_template
import os
from models import db, Asset, Portfolio

app = Flask(__name__)

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
db.init_app(app)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
    db.init_app(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)