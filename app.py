from flask import Flask, render_template, Blueprint, jsonify, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
import logging
from logging.handlers import RotatingFileHandler


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
db = SQLAlchemy(app)


# Setup logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


# Set your Alpha Vantage API key here
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'your_alpha_vantage_api_key')


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
    payout_months = db.Column(db.String, nullable=True, default="1,4,7,10")  # Default to quarterly payouts
    dividend_yield = db.Column(db.Float, nullable=False, default=0.01) # To be replaced with a real dividend yield
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

# https://www.alphavantage.co/documentation/#symbolsearch
def fetch_dividend_yield(asset_name):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={asset_name}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    data = response.json()

    # Logging statement to log the response
    app.logger.info(f"Response from Alpha Vantage for {asset_name}: {data}")

    time_series = data.get('Monthly Adjusted Time Series')
    if not time_series:
        app.logger.info(f"No time series data available for {asset_name}")
        return None  # No time series data available

    annual_dividend = 0.0
    months_counted = 0

    # Iterate over the last 12 months to sum up the dividends
    for date in sorted(time_series.keys(), reverse=True)[:12]:
        monthly_data = time_series[date]
        dividend = float(monthly_data.get('7. dividend amount', 0.0))
        annual_dividend += dividend
        months_counted += 1

    if months_counted == 0:
        app.logger.info(f"No dividend data available for {asset_name}")
        return None  # No dividend data available

    # Get the most recent closing price
    latest_data = next(iter(time_series.values()))
    latest_close = float(latest_data.get('4. close', 0.0))

    if latest_close == 0.0:
        app.logger.info(f"No closing price available for {asset_name}")
        return None  # No closing price available

    # Calculate the annual dividend yield
    dividend_yield = (annual_dividend / latest_close) * 100
    return dividend_yield




@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        name = request.form['name']
        value = request.form.get('value', type=float)
        portfolio_id = request.form.get('portfolio_id', type=int)
        if name and value is not None:
            dividend_yield = fetch_dividend_yield(name)
            if dividend_yield is None:
                return 'Asset does not pay a dividend and cannot be added', 400  # Handle non-dividend paying assets
            new_asset = Asset(name=name, value=value, portfolio_id=portfolio_id, dividend_yield=dividend_yield)
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

def calculate_dividend(asset):
    return asset.value * (asset.dividend_yield / 100)  # Assuming dividend_yield is a percentage

@app.route('/portfolios', methods=['GET', 'POST'])
def portfolios():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            new_portfolio = Portfolio(name=name)
            db.session.add(new_portfolio)
            db.session.commit()
        return redirect(url_for('portfolios'))
    
    portfolios = Portfolio.query.all()
    portfolio_data = []
    for portfolio in portfolios:
        portfolio_info = {
            'id': portfolio.id,
            'name': portfolio.name,
            'assets': []
        }
        for asset in portfolio.assets:
            dividend = calculate_dividend(asset)
            portfolio_info['assets'].append({
                'name': asset.name,
                'value': asset.value,
                'dividend_yield': asset.dividend_yield,
                'dividend': dividend
            })
        portfolio_data.append(portfolio_info)
    return render_template('portfolios.html', portfolios=portfolio_data)

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

@app.route('/dividends/<int:portfolio_id>', methods=['GET'])
def get_dividends(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    dividends = []
    for asset in portfolio.assets:
        dividend = calculate_dividend(asset)
        dividends.append({'name': asset.name, 'dividend': dividend})
    return jsonify(dividends)

@app.route('/portfolio/<int:portfolio_id>/dividends', methods=['GET'])
def portfolio_dividends(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    dividends = []
    for asset in portfolio.assets:
        dividend = calculate_dividend(asset)
        dividends.append({'name': asset.name, 'dividend': dividend})
    return render_template('portfolio_dividends.html', portfolio=portfolio, dividends=dividends)

from collections import defaultdict

@app.route('/dividend_calendar', methods=['GET'])
def dividend_calendar():
    portfolios = Portfolio.query.all()
    monthly_dividends = defaultdict(list)

    for portfolio in portfolios:
        for asset in portfolio.assets:
            if asset.dividend_yield is None or asset.dividend_yield <= 0:
                continue  # Skip assets without a dividend
            payout_months = asset.payout_months or "1,4,7,10"  # Default to quarterly if None
            for month in payout_months.split(','):
                month = int(month)
                monthly_dividends[month].append({
                    'name': asset.name,
                    'amount': calculate_dividend(asset) / len(payout_months.split(','))  # Equal payouts across specified months
                })

    # Convert defaultdict to regular dict for JSON serialization
    monthly_dividends = dict(monthly_dividends)
    return render_template('dividend_calendar.html', monthly_dividends=monthly_dividends)


from calendar import month_name as month_names

@app.context_processor
def utility_processor():
    def month_name(month_number):
        return month_names[month_number]
    return dict(month_name=month_name)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
