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
from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

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
    current_price = db.Column(db.Float, nullable=True)  # Current market price of the asset
    purchase_price = db.Column(db.Float, nullable=True)  # Purchase price of the asset
    purchase_date = db.Column(db.Date, nullable=True)  # Purchase date of the asset
    sector = db.Column(db.String(100), nullable=True)  # Sector or industry of the asset
    annual_dividend = db.Column(db.Float, nullable=True)  # Annual dividend paid per share
    dividend_yield = db.Column(db.Float, nullable=False, default=0.01)  # Dividend yield
    dividend_frequency = db.Column(db.String(50), nullable=False, default='quarterly')  # Dividend frequency
    dividend_growth = db.Column(db.Float, nullable=False, default=0.0)  # Dividend growth rate
    last_dividend_amount = db.Column(db.Float, nullable=False, default=0.0)  # Last dividend amount per share
    last_dividend_date = db.Column(db.Date, nullable=True)  # Last dividend payment date
    ex_dividend_date = db.Column(db.Date, nullable=True)  # Ex-dividend date
    payment_date = db.Column(db.Date, nullable=True)  # Payment date
    currency = db.Column(db.String(10), nullable=True)  # Currency of the asset and dividends
    dividend_payout_ratio = db.Column(db.Float, nullable=True)  # Dividend payout ratio
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=True)

    def __repr__(self):
        return (f"Asset('{self.name}', {self.shares} shares, {self.dividend_yield}% yield, "
                f"{self.dividend_frequency}, {self.dividend_growth}% growth, "
                f"{self.last_dividend_amount} last dividend, {self.last_dividend_date} last dividend date, "
                f"{self.ex_dividend_date} ex-dividend date, {self.payment_date} payment date, "
                f"{self.current_price} current price, {self.purchase_price} purchase price, "
                f"{self.purchase_date} purchase date, {self.sector} sector, {self.annual_dividend} annual dividend, "
                f"{self.currency} currency, {self.dividend_payout_ratio} payout ratio)")


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



def fetch_dividend_yield(asset_name):
    stock = yf.Ticker(asset_name)
    try:
        dividend_yield = stock.info['dividendYield'] * 100  # Convert to percentage
    except KeyError:
        app.logger.info(f"No dividend yield available for {asset_name}")
        return None
    return dividend_yield

@app.route('/assets')
def assets():
    assets = Asset.query.all()
    return render_template('assets.html', assets=assets)

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        shares_str = request.form.get('shares')
        current_price_str = request.form.get('current_price')
        purchase_price_str = request.form.get('purchase_price')
        purchase_date_str = request.form.get('purchase_date')
        sector = request.form.get('sector')
        annual_dividend_str = request.form.get('annual_dividend')
        dividend_yield_str = request.form.get('dividend_yield')
        dividend_frequency = request.form.get('dividend_frequency')
        dividend_growth_str = request.form.get('dividend_growth')
        last_dividend_amount_str = request.form.get('last_dividend_amount')
        last_dividend_date_str = request.form.get('last_dividend_date')
        ex_dividend_date_str = request.form.get('ex_dividend_date')
        payment_date_str = request.form.get('payment_date')
        currency = request.form.get('currency')
        dividend_payout_ratio_str = request.form.get('dividend_payout_ratio')
        portfolio_id = request.form.get('portfolio_id', type=int)

        # Convert numerical and date fields
        shares = float(shares_str) if shares_str else None
        current_price = float(current_price_str) if current_price_str else None
        purchase_price = float(purchase_price_str) if purchase_price_str else None
        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d') if purchase_date_str else None
        annual_dividend = float(annual_dividend_str) if annual_dividend_str else None
        dividend_yield = float(dividend_yield_str) if dividend_yield_str else 0.01
        dividend_growth = float(dividend_growth_str) if dividend_growth_str else 0.0
        last_dividend_amount = float(last_dividend_amount_str) if last_dividend_amount_str else 0.0
        last_dividend_date = datetime.strptime(last_dividend_date_str, '%Y-%m-%d') if last_dividend_date_str else None
        ex_dividend_date = datetime.strptime(ex_dividend_date_str, '%Y-%m-%d') if ex_dividend_date_str else None
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d') if payment_date_str else None
        dividend_payout_ratio = float(dividend_payout_ratio_str) if dividend_payout_ratio_str else None

        if name and shares is not None and portfolio_id is not None:
            new_asset = Asset(
                name=name,
                shares=shares,
                current_price=current_price,
                purchase_price=purchase_price,
                purchase_date=purchase_date,
                sector=sector,
                annual_dividend=annual_dividend,
                dividend_yield=dividend_yield,
                dividend_frequency=dividend_frequency,
                dividend_growth=dividend_growth,
                last_dividend_amount=last_dividend_amount,
                last_dividend_date=last_dividend_date,
                ex_dividend_date=ex_dividend_date,
                payment_date=payment_date,
                currency=currency,
                dividend_payout_ratio=dividend_payout_ratio,
                portfolio_id=portfolio_id
            )
            db.session.add(new_asset)
            db.session.commit()
            app.logger.info(
                f"Added new asset: {new_asset.name}, Shares: {new_asset.shares}, Current Price: {new_asset.current_price}, "
                f"Purchase Price: {new_asset.purchase_price}, Purchase Date: {new_asset.purchase_date}, Sector: {new_asset.sector}, "
                f"Annual Dividend: {new_asset.annual_dividend}, Dividend Yield: {new_asset.dividend_yield}, "
                f"Dividend Frequency: {new_asset.dividend_frequency}, Dividend Growth: {new_asset.dividend_growth}, "
                f"Last Dividend Amount: {new_asset.last_dividend_amount}, Last Dividend Date: {new_asset.last_dividend_date}, "
                f"Ex-Dividend Date: {new_asset.ex_dividend_date}, Payment Date: {new_asset.payment_date}, "
                f"Currency: {new_asset.currency}, Dividend Payout Ratio: {new_asset.dividend_payout_ratio}, "
                f"Portfolio ID: {new_asset.portfolio_id}"
            )
            return redirect(url_for('modify_portfolio', id=portfolio_id))
        else:
            app.logger.warning('Missing data: Name, Shares, Portfolio ID not provided or invalid')
            return 'Missing data', 400
    else:
        portfolios = Portfolio.query.all()
        app.logger.info(f"Portfolios: {portfolios}")
        return render_template('add_asset.html', portfolios=portfolios)



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
