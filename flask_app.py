"""
Prospect Capital Candidate Project

This module defines the web server and API for inserting stock buy/sell transactions into a database and 
viewing the resulting positions. 
It is currently hosted at joaladwig.pythonanywhere.com with the following routes:
    /positions
    /positionsbysector
    /transactions
    /securities
    /reset
    
The credentials for the database are included in plain text in the SQLALCHEMY_DATABASE_URI string for the
examiner to connect to the database if they would like. 

@author: Joa Ladwig
@date: 20241115
"""

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from models.models import Stock, Transaction


# This is the Flask instance of our web server
app = Flask(__name__)

# Database connection info. In a real environment/project, these would be saved as environment variables
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="joaladwig",
    password="insecurepassword",
    hostname="joaladwig.mysql.pythonanywhere-services.com",
    databasename="joaladwig$default",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database ORM object 
db = SQLAlchemy(app)


# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')


# Route for positions page
@app.route('/positions')
def positions():
    # NOTE: In SQLAlchemy, outer join is the same as left join
    # Group by stock ticker, sum of shares, filtering results where share count is 0. Ex: Buy 10 MSFT, Sell 10 MSFT, total shares is zero, so there is no position shown.
    pos = db.session.query(Transaction.ticker,
                           Stock.sector,
                           db.func.sum(Transaction.shares).label('Total_Shares')).outerjoin(Stock, Transaction.ticker == Stock.ticker).group_by(Transaction.ticker).having(db.func.sum(Transaction.shares) != 0).all()

    return render_template('positions.html', grouped_pos=pos)


# Route for positions by sector
@app.route('/positionsbysector')
def positionsbysector():
    # Similar to /positions query. Group by sector, sum of shares, filtering results where share count is 0.
    sector = db.session.query(Transaction.ticker, Stock.sector, db.func.sum(Transaction.shares).label('Total_Shares')).outerjoin(Stock, Transaction.ticker == Stock.ticker).group_by(Stock.sector).having(db.func.sum(Transaction.shares) != 0).all()
    return render_template('positionsbysector.html', grouped_sectors=sector)


# Route for transactions
@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    # Going to the web page via the URL is a GET request, and clicking 'Submit' is a POST request. This only executes after clicking on the button.
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        # Check that ticker is present in the Stock table
        if ticker not in Stock.ticker.query.all():
            return redirect(url_for('transactions'))
        direction = request.form['direction'].upper()
        shares = float(request.form['shares'])
        # Invert to negative if the user is selling
        if direction == 'SELL':
            shares *= -1
        price = request.form['price']

        # Construct and add new row to Transaction database. ID column is auto-incremented
        new_tx = Transaction(ticker=ticker, direction=direction, shares=shares, price=price)
        db.session.add(new_tx)
        db.session.commit()
        
        # Return to the main /transactions page
        return redirect(url_for('transactions'))

    return render_template('transactions.html', transactions=Transaction.query.all())


# Route for securities
@app.route('/securities')
def securities():
    return render_template('securities.html', stocks=Stock.query.all())


# Route for reset
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    # If 'Reset' button is pressed, truncate the Transaction table in the database
    if request.method == 'POST':
        with db.engine.connect() as connection:
            connection.execute("TRUNCATE TABLE transaction")
            return redirect(url_for('reset'))

    return render_template('reset.html')


