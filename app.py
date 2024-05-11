from flask import Flask, render_template, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'

db = SQLAlchemy(app)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Asset('{self.name}')"

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Portfolio('{self.name}')"

main = Blueprint('main', __name__)

@main.route('/')
def hello_world():
    return 'Hello, World from DiviDash!'

@main.route('/portfolios', methods=['GET'])
def get_portfolios():
    portfolios = Portfolio.query.all()
    return jsonify([{'id': p.id, 'name': p.name} for p in portfolios])

app.register_blueprint(main)

@app.route('/')
def index():
    assets = Asset.query.all()
    portfolios = Portfolio.query.all()
    return render_template('index.html', assets=assets, portfolios=portfolios)

@app.route('/assets')
def assets():
    assets = Asset.query.all()
    return render_template('assets.html', assets=assets)

@app.route('/portfolios')
def portfolios():
    portfolios = Portfolio.query.all()
    return render_template('portfolios.html', portfolios=portfolios)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)