from flask import Flask, render_template, Blueprint, jsonify, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
db = SQLAlchemy(app)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Asset('{self.name}', {self.value})"

with app.app_context():
    db.create_all()


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Portfolio('{self.name}')"

main = Blueprint('main', __name__)


from werkzeug.routing import BuildError

@main.route('/')
def hello_world():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    links = []
    for rule in app.url_map.iter_rules():
        try:
            url = url_for(rule.endpoint, _external=True, **{arg: 'dummy' for arg in rule.arguments})
        except BuildError:
            url = None
        links.append((url, rule.endpoint))
    return render_template('index.html', current_time=current_time, links=links)


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

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        name = request.form['name']
        value = request.form.get('value', type=float)
        if name and value is not None:
            new_asset = Asset(name=name, value=value)
            db.session.add(new_asset)
            db.session.commit()
            return redirect(url_for('assets'))
    elif request.method == 'GET':
        return render_template('add_asset.html')
    return 'Missing data', 400


@app.route('/portfolios')
def portfolios():
    portfolios = Portfolio.query.all()
    return render_template('portfolios.html', portfolios=portfolios)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)