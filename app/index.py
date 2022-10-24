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
from .models.review import Review

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

@bp.route('/purchase', methods = ['GET', 'POST'])
def purchases():
    form = SearchBarForm()
    if current_user.is_authenticated:
        #get all purchases
        purchases = Purchase.get_purchases(current_user.id)
    else:
        purchases = None

    query_purchases = []
    if form.validate_on_submit():
        query_purchases = Purchase.get_purchases(form.query.data)

    return render_template('purchase.html', purchases = purchases, query_purchases = query_purchases, form = form)

@bp.route('/review', methods = ['GET', 'POST'])
def reviews():
    form = SearchBarForm()
    if current_user.is_authenticated:
        #get all reviews
        your_reviews = Review.get_recent_reviews(current_user.id)
        your_seller_reviews = Review.get_seller_reviews(current_user.id)
    else:
        your_reviews = None
        your_seller_reviews = None

    query_reviews = []
    query_seller_review = []
    if form.validate_on_submit():
        query_reviews = Review.get_recent_reviews(form.query.data)
        query_seller_review = Review.get_seller_reviews(form.query.data)
    
    # render review page (shows reviews)
    
    return render_template('review.html', 
                            query_reviews = query_reviews,
                            query_seller_review = query_seller_review,
                            your_reviews = your_reviews,
                            your_seller_reviews = your_seller_reviews,
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

@bp.route('/product', methods=['GET', 'POST'])
def product_page():
    form = SearchBarForm()
    # if query submitted
    product = []
    if form.validate_on_submit():
        print(form.query, file=sys.stderr)
        
        product = Product.get_top_k(form.query.data)
        #cart = Cart.get_all_in_cart_by_pid(current_user.id, form.query.data)
        
        if not product:
            product = []

        return render_template('product.html',
                            product = product, form = form)

    # default: render full cart
    return render_template('product.html', 
                            product = product, form = form)

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')

