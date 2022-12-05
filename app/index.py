from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
import sys
import os
from io import BytesIO

from flask import current_app as app

from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)

#Main route to Home Page
@bp.route('/', methods = ['GET', 'POST'])
def index():
    # get all available products for sale:
    products = Product.get_all()
    products = update_image(products)
    query_form = SearchBarForm()
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    
    featured_products = Product.get_top_k(8)
    featured_products = update_image(featured_products)
    if query_form.validate_on_submit():
        search_products = Product.query_amount(query_form.query.data, query_form.category.data, query_form.price.data=="Ascending")
        search_products = update_image(search_products)
        return render_template('index.html',
                            featured_products = featured_products,
                           avail_products=search_products,
                           purchase_history=purchases,
                           form = query_form)

    # render the page by adding information to the index.html file
    return render_template('index.html',
                            featured_products = featured_products,
                           avail_products=products,
                           purchase_history=purchases,
                           form=query_form)


#adds image to each product
def update_image(products):
    for item in products:
        if (item.image.tobytes() == b'0'):
            item.image = 'static/default.jpg'
        else:
            try:
                item.image = 'static/' + str(item.id) + '.png'  
            except:
                item.image = 'static/' + str(item.pid) + '.png'  
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


class SearchBarForm(FlaskForm):
    query = StringField('Search Query')
    category = SelectField('Category', choices=["", "Home Goods", "Food", "Electronics", "Cosmetics"])
    price = SelectField('Price', choices=["Ascending", "Descending"], validators=[DataRequired()])
    submit = SubmitField('Search')


