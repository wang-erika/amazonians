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
from .models.cart import Cart
from .models.order import Order

from flask import Blueprint
bp = Blueprint('buy', __name__)


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
def view_orders_cart_page():
    orders_map = Cart.order_map_purchases(current_user.id)
    return render_template('cart_order.html', 
                                orders_map=orders_map)

@bp.route('/cart/order/', methods=['GET', 'POST'])
def orders_cart_page():
    #todo ADD FLASHES   
    flash('Does this work')
    cart = Cart.get_all_in_cart(current_user.id)
    total = Cart.get_total_price_in_cart(current_user.id)
    if total[0][0]:
        total = float(total[0][0])
    else:
        total = 0
    flash(total)
    # Check total
    flash(Cart.check_balance(current_user.id, total))

    # If total is affordable
    # && all cart items have enough quantity
    # && user cart is not empty
    if (Cart.check_balance(current_user.id, total) and Cart.check_quantity(cart)):
        # Create Order
        oid = Cart.add_order_to_orders(current_user.id)
        # Add items to Purchases (referencing oid)
        Cart.add_items_to_purchases(cart, oid)

        # Clear Cart
        Cart.delete_all_cart_items(cart)

        orders = Order.get_orders_by_uid(current_user.id)

        map = Cart.order_map_purchases(current_user.id, orders)

        return render_template('cart_order.html', 
                                cart = cart, 
                                total = total,
                                map=map)
                        
    
    return render_template('cart_order.html', 
                            cart = cart, 
                            total = total) 

    
class EditProductQuantityForm(FlaskForm):
    quantity = IntegerField('New quantity', validators=[])
    submit = SubmitField('Update')

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')



