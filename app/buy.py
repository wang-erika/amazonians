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
from .models.review import Review
from .models.later import Later

from flask import Blueprint
bp = Blueprint('buy', __name__)

my_formatter = "{0:.2f}"
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
        saved_for_later = Later.get_all_in_saved_for_later(current_user.id)
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
                            cart = cart, saved_for_later = saved_for_later, total = my_formatter.format(total))

#move cart item into later cart 
@bp.route('/cart/saved/<pid>', methods=['GET', 'POST'])
def move_cart_item(pid):
    #todo ADD FLASHES
    #get relevent into for the insertion
    sid = Product.get_sid_from_pid(pid)
    quantity = Cart.get_quantity(pid, current_user.id)[0][0]
    
    #add into save for later table
    Later.add_into_saved_for_later(current_user.id, sid, pid, quantity)
    
    #delete from cart
    Cart.delete_cart_item(current_user.id, pid)
    flash('Product removed from your cart and into saved for later.')
    return redirect(url_for('buy.cart_page'))

#move later item back into cart
@bp.route('/cart/backcart/<pid>', methods=['GET', 'POST'])
def move_later_item(pid):
    #todo ADD FLASHES   
    #get relevent into for the insertion
    sid = Product.get_sid_from_pid(pid)
    quantity = Later.get_later_quantity(pid, current_user.id)[0][0]
    
    #add back into cart table
    Cart.add_product_to_cart(current_user.id, sid, pid, quantity)
    
    #delete from later table
    Later.delete_later_item(current_user.id, pid)
    flash('Product removed from saved for later into cart.')
    return redirect(url_for('buy.cart_page'))

#viewing item panels in later table
@bp.route('/cart/later/<pid>', methods=['GET', 'POST'])
def view_later_item(pid):
    #todo ADD FLASHES
    stats = Review.get_product_stats(pid)
    num_reviews = Review.get_number_ratings(pid)
    summary_reviews = Review.get_summary_reviews(pid)
    
    edit_quantity_form = EditProductQuantityForm()
    item = Later.get_all_in_later_by_pid(current_user.id, pid)
    if (item.image.tobytes() == b'0'):
        item.image = '../../static/default.jpg'
    else:
        item.image = '../../static/' + str(item.pid) + '.png'
    print(item.image)
    
    if edit_quantity_form.validate_on_submit():
        Later.edit_later_item(current_user.id, pid, edit_quantity_form.quantity.data)
        return redirect(url_for('buy.cart_page'))
    
    return render_template('later_item.html',
                            item = item,
                            edit_quantity_form = edit_quantity_form,
                            stats = stats,
                            num_reviews = num_reviews,
                            summary_reviews = summary_reviews)
    
@bp.route('/cart/details/<pid>', methods=['GET', 'POST'])
def view_cart_item(pid):
    #todo ADD FLASHES
    stats = Review.get_product_stats(pid)
    num_reviews = Review.get_number_ratings(pid)
    summary_reviews = Review.get_summary_reviews(pid)


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
                            edit_quantity_form = edit_quantity_form,
                            stats = stats,
                            num_reviews = num_reviews,
                            summary_reviews = summary_reviews)
    
@bp.route('/cart/laterdelete/<pid>', methods=['GET', 'POST'])
def delete_later_item(pid):
    #todo ADD FLASHES   
    Later.delete_later_item(current_user.id, pid)
    flash('Product removed from your cart.')
    return redirect(url_for('buy.cart_page'))

@bp.route('/cart/delete/<pid>', methods=['GET', 'POST'])
def delete_cart_item(pid):
    #todo ADD FLASHES   
    Cart.delete_cart_item(current_user.id, pid)
    flash('Product removed from your cart.')
    return redirect(url_for('buy.cart_page'))

@bp.route('/cart/checkout', methods=['GET', 'POST'])
def orders_cart_page_checkout():
    #todo ADD FLASHES   
    cart = Cart.get_all_in_cart(current_user.id)
    total = Cart.get_total_price_in_cart(current_user.id)
    if total[0][0]:
        total = float(total[0][0])
    else:
        total = 0
    # Check total

    # If total is affordable
    # && all cart items have enough quantity
    # && user cart is not empty
    if (Cart.check_balance(current_user.id, total) and Cart.check_quantity(cart) and cart):
        # Create Order
        oid = Cart.add_order_to_orders(current_user.id)
        
        #edit balance for user
        Cart.edit_balance_user(current_user.id, total)
        
        #edit balance for seller
        Cart.edit_balance_seller(cart)
        
        #edit quantity for seller
        Cart.edit_quantity(cart)
        
        
        # Add items to Purchases (referencing oid)
        Cart.add_items_to_purchases(cart, oid)

        # Clear Cart
        Cart.delete_all_cart_items(cart)

        orders = Order.get_orders_by_uid(current_user.id)

        map = Cart.order_map_purchases(current_user.id, orders)

        return redirect(url_for('buy.orders_cart_page'))
                        
    #EDIT
    flash("You cannot afford, all cart items do not have enough quantity or your cart is empty")
    return render_template('cart.html', 
                            cart = cart, 
                            total = my_formatter.format(total)) 

@bp.route('/cart/orders/', methods=['GET', 'POST'])
def orders_cart_page():
    orders = Order.get_orders_by_uid(current_user.id)
    map = Cart.order_map_purchases(current_user.id, orders)
    
    return render_template('cart_order.html',
                                map=map)
    

    
class EditProductQuantityForm(FlaskForm):
    quantity = IntegerField('New quantity', validators=[])
    submit = SubmitField('Update')

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')



