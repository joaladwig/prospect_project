from flask_sqlalchemy import SQLAlchemy
from enum import Enum

# Database ORM object 
db = SQLAlchemy(app)


# Enumeration to store our two transaction types
class DirEnum(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


# Model of the 'stock' table in the database
# Three columns: ID, Ticker, Sector
class Stock(db.Model):
    __tablename__ = "stock"

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(5))
    sector = db.Column(db.String(4096))


# Model of the 'transaction' table in the database
# Five columns: ID, Ticker, Direction, Shares, Price
class Transaction(db.Model):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(5))
    direction = db.Column(db.Enum(DirEnum))
    shares = db.Column(db.Numeric(precision=10, scale=2))
    price = db.Column(db.Numeric(precision=10, scale=2))