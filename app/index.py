from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from flask import current_app as app
from flask import request
from flask_paginate import Pagination, get_page_parameter

from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)

PAGE_SIZE = 30

#Main route to Home Page
@bp.route('/', methods = ['GET', 'POST'])
def index():
    # get all avaliable products 
    page = request.args.get(get_page_parameter(), type=int, default=1)
    products = Product.get_all()
    # update the image
    products = update_image(products)
    # create the pagination
    pagination = Pagination(page=page, total=len(products), search=False, per_page=PAGE_SIZE)
    # form for queries
    query_form = SearchBarForm()
    products = products[(page-1)*PAGE_SIZE:min(page*PAGE_SIZE, len(products))]

    # get the top 8 most expensive products to feature in the carosel
    featured_products = Product.get_top_k(8)
    featured_products = update_image(featured_products)

    # processing a query
    if query_form.validate_on_submit():
        cat = query_form.category.data
        query = query_form.query.data
        # if certain fields are not filled
        if len(query) == 0:
            query = "None"
        if len(cat) == 0:
            cat = "None"
        # go to the search endpoint
        return redirect(url_for('index.search', query=query, 
                        category=cat,
                        price=query_form.price.data))

    # render the page by adding information to the index.html file
    return render_template('index.html',
                            featured_products = featured_products,
                           avail_products=products,
                           form=query_form,
                           pagination=pagination)

# this page is the same as index.html, just with the results from the search
@bp.route('/search/<query>/<category>/<price>', methods = ['GET', 'POST'])
def search(query, category, price):
    # handling fields that are not given
    if category == "None":
        category = ""
    if query == "None":
        query = ""
    
    # get the curent page and create the pagination, along with querying
    page = request.args.get(get_page_parameter(), type=int, default=1)
    products = Product.query_amount(query, category, price=="Ascending")
    products = update_image(products)
    pagination = Pagination(page=page, total=len(products), search=False, per_page=PAGE_SIZE)

    # get only the necessary products
    products = products[(page-1)*PAGE_SIZE:min(page*PAGE_SIZE, len(products))]

    # query form if you want to query again
    query_form = SearchBarForm()

    # get the top 8 most expensive products  
    featured_products = Product.get_top_k(8)
    featured_products = update_image(featured_products)

    if query_form.validate_on_submit():
        # process another query request
        cat = query_form.category.data
        query = query_form.query.data
        if len(query) == 0:
            query = "None"
        if len(cat) == 0:
            cat = "None"
        return redirect(url_for('index.search', query=query, 
                        category=cat,
                        price=query_form.price.data))

    # render the page by adding information to the index.html file
    return render_template('index.html',
                        featured_products = featured_products,
                           avail_products=products,
                           form=query_form,
                           pagination=pagination)




#adds image to each product
def update_image(products):
    for item in products:
        if (item.image.tobytes() == b'0'):
            item.image = '../../../static/default.jpg'
        else:
            try:
                item.image = '../../../static/' + str(item.id) + '.png'  
            except:
                item.image = '../../../static/' + str(item.pid) + '.png'  
    return products

#get recent purchases
@bp.route('/purchase', methods = ['GET', 'POST'])
def purchases():
    form = SearchBarForm()
    if current_user.is_authenticated:
        #get all purchases
        purchases = Purchase.get_purchases(current_user.id)
    else:
        purchases = None

    return render_template('purchase.html', purchases = purchases)

# this form is used for queries of products
class SearchBarForm(FlaskForm):
    query = StringField('Search Query')
    category = SelectField('Category', choices=["", "Home Goods", "Food", "Electronics", "Cosmetics"])
    price = SelectField('Price', choices=["Ascending", "Descending"], validators=[DataRequired()])
    submit = SubmitField('Search')


