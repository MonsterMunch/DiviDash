from flask import Flask, render_template, Blueprint, jsonify, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
import yfinance as yf
import calendar
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividash.db'
db = SQLAlchemy(app)

# Setup logging
log_file = 'app.log'
handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)  # Set to INFO to capture more detailed logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)  # Set to INFO to capture more detailed logs

# Define the Portfolio and Asset models
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    assets = db.relationship('Asset', backref='portfolio', lazy=True)

    def __repr__(self):
        return f"Portfolio('{self.name}')"

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    shares = db.Column(db.Float, nullable=False)  # Number of shares
    dividend_yield = db.Column(db.Float, nullable=False, default=0.01) # To be replaced with a real dividend yield
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=True)

    def __repr__(self):
        return f"Asset('{self.name}', {self.shares} shares)"

# Initialize the database
with app.app_context():
    db.create_all()

# Context processor to add month_name function to templates
@app.context_processor
def utility_processor():
    def month_name(month_number):
        return calendar.month_name[month_number]
    return dict(month_name=month_name)

# Define the main blueprint and routes
main = Blueprint('main', __name__)

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

def fetch_dividend_yield(asset_name):
    stock = yf.Ticker(asset_name)
    try:
        dividend_yield = stock.info['dividendYield'] * 100  # Convert to percentage
    except KeyError:
        app.logger.info(f"No dividend yield available for {asset_name}")
        return None
    return dividend_yield


@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        name = request.form.get('name')
        shares_str = request.form.get('shares')  # Get the raw string value
        portfolio_id = request.form.get('portfolio_id', type=int)

        # Log the retrieved form data before conversion
        app.logger.info(f"Raw form data - Name: {name}, Shares: {shares_str}, Portfolio ID: {portfolio_id}")

        try:
            shares = float(shares_str) if shares_str else None
        except ValueError:
            shares = None
            app.logger.warning('Invalid number of shares provided')

        app.logger.info(f"Converted form data - Name: {name}, Shares: {shares}, Portfolio ID: {portfolio_id}")

        if name and shares is not None and portfolio_id is not None:
            dividend_yield = fetch_dividend_yield(name)
            if dividend_yield is None:
                app.logger.info(f"No dividend yield available for {name}")
                return 'Asset does not pay a dividend or data is unavailable', 400  # Handle non-dividend paying assets
            new_asset = Asset(name=name, shares=shares, portfolio_id=portfolio_id, dividend_yield=dividend_yield)
            db.session.add(new_asset)
            db.session.commit()
            app.logger.info(f"Added new asset: {new_asset}")
            return redirect(url_for('modify_portfolio', id=portfolio_id))
        else:
            app.logger.warning('Missing data: Name, Shares, or Portfolio ID not provided')
            return 'Missing data', 400  # Ensure all fields are present
    else:
        portfolios = Portfolio.query.all()
        app.logger.info(f"Portfolios: {portfolios}")
        return render_template('modify_portfolio.html', portfolios=portfolios)


@app.route('/delete_asset/<int:id>', methods=['POST'])
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    portfolio_id = asset.portfolio_id
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('modify_portfolio', id=portfolio_id))

def calculate_dividend(asset):
    return asset.shares * (asset.dividend_yield / 100)  # Assuming dividend_yield is a percentage

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
            # Fetch the current price of the asset
            stock = yf.Ticker(asset.name)
            latest_price = stock.history(period='1d')['Close'].iloc[0]
            value = latest_price * asset.shares
            dividend_yield = fetch_dividend_yield(asset.name)
            if dividend_yield is None:
                dividend_yield = asset.dividend_yield  # Use the stored value if not available from yfinance
            dividend_yield = round(dividend_yield, 2)  # Round to two decimal places
            dividend = calculate_dividend(asset)
            portfolio_info['assets'].append({
                'id': asset.id,  # Ensure the id is included
                'name': asset.name,
                'shares': asset.shares,
                'dividend_yield': dividend_yield,
                'value': value,
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
    
    app.logger.info("Initialized monthly_dividends as an empty defaultdict(list)")

    for portfolio in portfolios:
        app.logger.info(f"Processing portfolio: {portfolio.name}")
        for asset in portfolio.assets:
            app.logger.info(f"Processing asset: {asset.name}")
            ticker = yf.Ticker(asset.name)
            dividends = ticker.dividends
            app.logger.info(f"Fetched dividends for {asset.name}: {dividends}")

            if dividends.empty:
                app.logger.info(f"No dividend data available for {asset.name}")
                continue  # Skip assets without a dividend

            for ex_date, amount in dividends.items():
                payment_month = (ex_date.month % 12) + 1  # Adding one to the ex-dividend month
                month_name = calendar.month_name[payment_month]
                app.logger.info(f"Adding dividend for {asset.name} in month {month_name} ({payment_month}): {amount}")
                monthly_dividends[payment_month].append({
                    'name': asset.name,
                    'amount': float(amount) * asset.shares  # Total dividend amount based on shares
                })

    # Sum the dividends for each month and asset
    summed_dividends = defaultdict(lambda: defaultdict(float))
    app.logger.info("Initialized summed_dividends as an empty defaultdict(lambda: defaultdict(float))")

    for month, dividends in monthly_dividends.items():
        month_name = calendar.month_name[month]
        app.logger.info(f"Processing dividends for month {month_name} ({month})")
        for dividend in dividends:
            summed_dividends[month][dividend['name']] += dividend['amount']
            app.logger.info(f"Summed dividends for {dividend['name']} in {month_name}: {summed_dividends[month][dividend['name']]}")

    # Convert summed dividends to the expected format
    final_dividends = defaultdict(list)
    app.logger.info("Initialized final_dividends as an empty defaultdict(list)")

    for month, assets in summed_dividends.items():
        month_name = calendar.month_name[month]
        for name, amount in assets.items():
            final_dividends[month].append({
                'name': name,
                'amount': amount
            })
            app.logger.info(f"Final dividend for {name} in {month_name}: {amount}")

    # Save the response to a JSON file for debugging
    response_data = {calendar.month_name[month]: dividends for month, dividends in final_dividends.items()}
    with open('dividend_calendar_debug.json', 'w') as f:
        json.dump(response_data, f, indent=4)
    app.logger.info("Saved the final dividend data to dividend_calendar_debug.json")

    return render_template('dividend_calendar.html', monthly_dividends=final_dividends)

# Define your models and other routes here as before...

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
