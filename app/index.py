from flask import render_template, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
import sys

from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all()
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases)

@bp.route('/sell', methods=['GET', 'POST'])
def inventory_page():
    form = SearchBarForm()
    if current_user.is_authenticated:
        # get all products they are selling
        inventory = Inventory.get_by_sid(current_user.id)
    else:
        inventory = None
    # render the search query if there is one
    query_inventory = []
    if form.validate_on_submit():
        query_inventory = Inventory.get_by_sid(form.query.data)
    
    # render Sell page (shows inventory)
    return render_template('inventory.html', 
                            inventory = inventory,
                            query_inventory = query_inventory,
                            form = form)

@bp.route('/purchases', methods = ['GET', 'POST'])
def purchases():
    form = SearchBarForm()
    if current_user.is_authenticated:
        #get all purchases
        purchase = Purchase.get_purchases(current_user.id)
    else:
        purchase = None
    
    return render_template('purchase.html', purchase = purchase, form = form)

@bp.route('/review', methods = ['GET', 'POST'])
def reviews():
    form = SearchBarForm()
    if current_user.is_authenticated:
        #get all reviews
        review = Review.get_recent_reviews(current_user.id)
    else:
        review = None

    query_review = []
    if form.validate_on_submit():
        query_review = Review.get_recent_reviews(form.query.data)
    
    # render review page (shows reviews)
    
    return render_template('review.html', 
                            review = review, 
                            query_review = query_review, 
                            form = form)

@bp.route('/cart', methods=['GET', 'POST'])
def cart_page():
    form = SearchBarForm()
    if current_user.is_authenticated:
        # get all products they are selling
        cart = Cart.get_all_in_cart(current_user.id)
    else:
        cart = []

    # if query submitted
    if form.validate_on_submit():
        print(form.query, file=sys.stderr)
        
        cart = Cart.get_all_in_cart(form.query.data)
        #cart = Cart.get_all_in_cart_by_pid(current_user.id, form.query.data)
        
        if not cart:
            cart = []

        return render_template('cart.html',
                            cart = cart, form = form)

    # default: render full cart
    return render_template('cart.html', 
                            cart = cart, form = form)

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')

