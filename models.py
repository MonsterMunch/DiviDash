from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    dividend_yield = db.Column(db.Float, nullable=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)

class PortfolioAsset(db.Model):
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), primary_key=True)
    allocation = db.Column(db.Float, nullable=False)
