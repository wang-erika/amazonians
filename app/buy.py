from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
import sys
from PIL import Image
from io import BytesIO
import os

from flask import current_app as app


from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.cart import Cart
from .models.review import Review
from .models.review import Seller_Review
from .models.order import Order

from flask import Blueprint
bp = Blueprint('buy', __name__)

@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all()
    products = update_image(products)
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

@bp.route('/cart', methods=['GET', 'POST'])
def cart_page():
    if current_user.is_authenticated:
        # get all products they are selling
        cart = Cart.get_all_in_cart(current_user.id)
        cart = update_image(cart)
        #total = Cart.get_total_price_in_cart(form.query.data)
        total = Cart.get_total_price_in_cart(current_user.id)
        if total[0][0]:
            total = float(total[0][0])
        else:
            total = 0
    else:
        cart = []
    
    #if edit form
    # default: render full cart
    return render_template('cart.html', 
                            cart = cart, total = total)

@bp.route('/cart/details/<pid>', methods=['GET', 'POST'])
def view_cart_item(pid):
    #todo ADD FLASHES
    edit_quantity_form = EditProductQuantityForm()
    item = Cart.get_all_in_cart_by_pid(current_user.id, pid)
    if (item.image.tobytes() == b'0'):
        item.image = '../../static/default.jpg'
    else:
        item.image = '../../static/' + str(item.pid) + '.png'
    print(item.image)
    
    if edit_quantity_form.validate_on_submit():
        flash('poop')
        Cart.edit_cart_item(current_user.id, pid, edit_quantity_form.quantity.data)
        return redirect(url_for('buy.cart_page'))
    
    return render_template('cart_item.html',
                            item = item,
                            edit_quantity_form = edit_quantity_form)

@bp.route('/cart/delete/<pid>', methods=['GET', 'POST'])
def delete_cart_item(pid):
    #todo ADD FLASHES   
    Cart.delete_cart_item(current_user.id, pid)
    flash('Product removed from your cart.')
    return redirect(url_for('buy.cart_page'))

@bp.route('/cart/order/', methods=['GET', 'POST'])
def orders_cart_page():
    #todo ADD FLASHES   
    cart = Cart.get_all_in_cart(current_user.id)
    total = Cart.get_total_price_in_cart(current_user.id)
    Cart.add_cart_to_orders(current_user.id)
    Cart.delete_all_cart_items(current_user.id)
    orders = Order.get_orders_by_uid(current_user.id)
    if total[0][0]:
        total = float(total[0][0])
    else:
        total = 0
    return render_template('cart_order.html', 
                            cart = cart, total = total, orders=orders)

    
class EditProductQuantityForm(FlaskForm):
    quantity = IntegerField('New quantity', validators=[])
    submit = SubmitField('Update')

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')



