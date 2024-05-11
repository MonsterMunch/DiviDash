from flask import Blueprint, jsonify, request, abort
from extensions import db
from models import Portfolio, Asset, PortfolioAsset

main = Blueprint('main', __name__)

@main.route('/')
def hello_world():
    return 'Hello, World from DiviDash!'

@main.route('/portfolios', methods=['GET'])
def get_portfolios():
    portfolios = Portfolio.query.all()
    return jsonify([{'id': p.id, 'name': p.name} for p in portfolios])

# Additional routes as needed
