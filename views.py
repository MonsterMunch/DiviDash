from app import db
from flask import render_template, request
from app import app
from models import Asset, Portfolio

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