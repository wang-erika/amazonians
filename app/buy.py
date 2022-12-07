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

# this method takes in the image information and determines its path to display
def update_image(products):
    for item in products:
        if (item.image.tobytes() == b'0'):
            item.image = '../../static/default.jpg'
        else:
            try:
                item.image = '../../static/' + str(item.id) + '.png'  
            except:
                item.image = '../../static/' + str(item.pid) + '.png'  
    return products

# this method creates the main cart page
@bp.route('/cart', methods=['GET', 'POST'])
def cart_page():
    if current_user.is_authenticated:
        # get all products that are currently in the cart and update the image
        cart = Cart.get_all_in_cart(current_user.id)
        cart = update_image(cart)

        # find all products are in currently in our saved for later
        saved_for_later = Later.get_all_in_saved_for_later(current_user.id)
        saved_for_later = update_image(saved_for_later)

        # get the total price of the cart
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
    # get the stats of the products and other information
    stats = Review.get_product_stats(pid)
    num_reviews = Review.get_number_ratings(pid)
    summary_reviews = Review.get_summary_reviews(pid)
    
    # changing how much we want in our cart
    edit_quantity_form = EditProductQuantityForm()
    item = Later.get_all_in_later_by_pid(current_user.id, pid)

    # image info
    if (item.image.tobytes() == b'0'):
        item.image = '../../static/default.jpg'
    else:
        item.image = '../../static/' + str(item.pid) + '.png'
    print(item.image)
    
    # checking if you change quantity
    if edit_quantity_form.validate_on_submit():
        # update quantity
        Later.edit_later_item(current_user.id, pid, edit_quantity_form.quantity.data)
        return redirect(url_for('buy.cart_page'))
    
    # later item view page
    return render_template('later_item.html',
                            item = item,
                            edit_quantity_form = edit_quantity_form,
                            stats = stats,
                            num_reviews = num_reviews,
                            summary_reviews = summary_reviews)

# view the cart item and its information
@bp.route('/cart/details/<pid>', methods=['GET', 'POST'])
def view_cart_item(pid):
    #todo ADD FLASHES
    # get the stats of the product
    stats = Review.get_product_stats(pid)
    num_reviews = Review.get_number_ratings(pid)
    summary_reviews = Review.get_summary_reviews(pid)

    # form for changing quanity of the product
    edit_quantity_form = EditProductQuantityForm()
    item = Cart.get_all_in_cart_by_pid(current_user.id, pid)

    # changing image info
    if (item.image.tobytes() == b'0'):
        item.image = '../../static/default.jpg'
    else:
        item.image = '../../static/' + str(item.pid) + '.png'
    print(item.image)
    
    # edit the cart item if quantity has changed
    if edit_quantity_form.validate_on_submit():
        Cart.edit_cart_item(current_user.id, pid, edit_quantity_form.quantity.data)
        return redirect(url_for('buy.cart_page'))
    
    return render_template('cart_item.html',
                            item = item,
                            edit_quantity_form = edit_quantity_form,
                            stats = stats,
                            num_reviews = num_reviews,
                            summary_reviews = summary_reviews)

#given a product id, delete it from the saved for later
@bp.route('/cart/laterdelete/<pid>', methods=['GET', 'POST'])
def delete_later_item(pid):  
    Later.delete_later_item(current_user.id, pid)
    flash('Product removed from your cart.')
    return redirect(url_for('buy.cart_page'))

#given a product id, delete it from the cart
@bp.route('/cart/delete/<pid>', methods=['GET', 'POST'])
def delete_cart_item(pid): 
    Cart.delete_cart_item(current_user.id, pid)
    flash('Product removed from your cart.')
    return redirect(url_for('buy.cart_page'))

#function to fascilitate orders submission
#does checks for order processing, processes order, saves cart information, and returns html
@bp.route('/cart/checkout', methods=['GET', 'POST'])
def orders_cart_page_checkout():
    #todo ADD FLASHES   
    cart = Cart.get_all_in_cart(current_user.id)
    cart = update_image(cart)
    saved_for_later = Later.get_all_in_saved_for_later(current_user.id)
    saved_for_later = update_image(saved_for_later)
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
    else:
    #EDIT
        flash("You cannot afford, all cart items do not have enough quantity or your cart is empty")
        return render_template('cart.html', 
                                cart = cart, 
                                saved_for_later=saved_for_later,
                                total = my_formatter.format(total)) 

#sets orders and map that stores associated information 
@bp.route('/cart/orders/', methods=['GET', 'POST'])
def orders_cart_page():
    orders = Order.get_orders_by_uid(current_user.id)
    map = Cart.order_map_purchases(current_user.id, orders)
    
    return render_template('cart_order.html',
                                map=map)
    
#edit quantity flaskform
class EditProductQuantityForm(FlaskForm):
    quantity = IntegerField('New quantity', validators=[])
    submit = SubmitField('Update')

#search flaskform
class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')



