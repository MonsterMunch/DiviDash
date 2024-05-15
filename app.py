from flask import Flask, render_template, Blueprint, jsonify, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
db = SQLAlchemy(app)

@app.route('/create_portfolio', methods=['POST'])
def create_portfolio():
    name = request.form['name']
    if name:
        new_portfolio = Portfolio(name=name)
        db.session.add(new_portfolio)
        db.session.commit()
        return redirect(url_for('main.hello_world'))
    return 'Missing data', 400

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    assets = db.relationship('Asset', backref='portfolio', lazy=True)

    def __repr__(self):
        return f"Portfolio('{self.name}')"

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=True)

    def __repr__(self):
        return f"Asset('{self.name}', {self.value})"
    
with app.app_context():
    db.create_all()

main = Blueprint('main', __name__)

from werkzeug.routing import BuildError

@main.route('/')
def hello_world():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    links = []
    for rule in app.url_map.iter_rules():
        try:
            placeholders = {arg: 1 if converter.__class__.__name__ == 'IntegerConverter' else 'dummy' for arg, converter in rule._converters.items()}
            url = url_for(rule.endpoint, _external=True, **placeholders)
        except BuildError:
            url = None
        links.append((url, rule.endpoint))
    return render_template('index.html', current_time=current_time, links=links)

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

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        name = request.form['name']
        value = request.form.get('value', type=float)
        portfolio_id = request.form.get('portfolio_id', type=int)
        if name and value is not None:
            new_asset = Asset(name=name, value=value, portfolio_id=portfolio_id)
            db.session.add(new_asset)
            db.session.commit()
            return redirect(url_for('modify_portfolio', id=portfolio_id))
    else:
        portfolios = Portfolio.query.all()
        return render_template('add_asset.html', portfolios=portfolios)
    return 'Missing data', 400

@app.route('/delete_asset/<int:id>', methods=['POST'])
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    portfolio_id = asset.portfolio_id
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('modify_portfolio', id=portfolio_id))

@app.route('/portfolios', methods=['GET', 'POST'])
def portfolios():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            new_portfolio = Portfolio(name=name)
            db.session.add(new_portfolio)
            db.session.commit()
        return redirect(url_for('portfolios'))
    else:
        portfolios = Portfolio.query.all()
        return render_template('portfolios.html', portfolios=portfolios)

@app.route('/modify_portfolio/<int:id>', methods=['GET', 'POST'])
def modify_portfolio(id):
    portfolio = Portfolio.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        if name:
            portfolio.name = name
            db.session.commit()
            return redirect(url_for('portfolios'))
    return render_template('modify_portfolio.html', portfolio=portfolio)

@app.route('/delete_portfolio/<int:id>', methods=['POST'])
def delete_portfolio(id):
    portfolio = Portfolio.query.get_or_404(id)
    db.session.delete(portfolio)
    db.session.commit()
    return redirect(url_for('portfolios'))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
