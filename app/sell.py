from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from datetime import datetime
import sys
from PIL import Image
from io import BytesIO
import os

from flask import current_app as app

from .models.inventory import Inventory
from .models.order import Order
from .models.purchase import Purchase
from .models.product import Product

from flask import Blueprint
bp = Blueprint('sell', __name__)


# MAIN ROUTE -- Sell page
@bp.route('/sell', methods=['GET', 'POST'])
def inventory_page():
    # Retrieve inventory products
    inventory = Inventory.get_by_sid(current_user.id)
    inventory = edit_inventory(inventory)
    
    # Render Sell page (shows inventory)
    return render_template('inventory.html', 
                            inventory = inventory)

# Take an inventory and configure the image
# Returns the inventory
def edit_inventory(inventory):
    for item in inventory:
        path = os.path.join(app.root_path, 'static/' + str(item.pid) + '.png')
        img = Image.open(BytesIO(item.image.tobytes()))
        img.save(path)
        item.image = 'static/' + str(item.pid) + '.png'
    return inventory

# Add page -- add new product to inventory
@bp.route('/sell/add', methods=['GET', 'POST'])
def add_to_inventory_page():
    # Create form
    add_form = AddProductToInventoryForm()

    # Redirect to main Sell page once form completed
    if add_form.validate_on_submit():
        if Inventory.add_new_inventory_item(current_user.id,
                                    add_form.name.data,
                                    add_form.image.data,
                                    add_form.category.data,
                                    add_form.unit_price.data,
                                    add_form.description.data,
                                    add_form.quantity.data,):
            
            # Success message
            msg = 'Success! Product "{name}" added to your inventory.'.format(name = add_form.name.data)
            flash(msg)
            
            return redirect(url_for('sell.inventory_page'))

    # Render Add page with form
    return render_template('sell/add_to_inventory.html', 
                            add_form = add_form)

class AddProductToInventoryForm(FlaskForm):
    name = StringField('Product name', validators=[])
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    category = SelectField('Category', choices=["Home Goods", "Food", "Electronics", "Cosmetics"])
    unit_price = DecimalField('Unit price', validators=[])
    description = StringField('Description', validators=[])
    quantity = IntegerField('Quantity in stock', validators=[])
    
    submit = SubmitField('Create and add')

# Details page -- view an inventory product's details
@bp.route('/sell/details/<pid>', methods=['GET', 'POST'])
def view_inventory_item(pid):
    # Create edit form
    edit_quantity_form = EditProductQuantityForm()

    # Get product details
    item = Inventory.get_by_sid_and_pid(current_user.id, pid)

    # Format image path
    item.image = 'static/' + str(item.pid) + '.png'

    # Re-render page if edit form is submitted
    if edit_quantity_form.validate_on_submit():
        Inventory.edit_inventory_item(current_user.id,
                                    pid,
                                    edit_quantity_form.quantity.data)
        
        msg = 'Product quantity updated to {q}.'.format(q = edit_quantity_form.quantity.data)
        flash(msg)
        return redirect(url_for('sell.inventory_page'))

    # Render Details page
    return render_template('sell/inventory_item.html',
                            item = item,
                            edit_quantity_form = edit_quantity_form)

class EditProductQuantityForm(FlaskForm):
    quantity = IntegerField('New quantity', validators=[])
    submit = SubmitField('Update')

# Delete route (no page) -- delete product from inventory
@bp.route('/sell/delete/<pid>', methods=['GET', 'POST'])
def delete_inventory_item(pid):
    # Delete product from database
    Inventory.delete_inventory_item(current_user.id, pid)

    # Success message
    flash('Product removed from your inventory.')

    # Re-render Sell page
    return redirect(url_for('sell.inventory_page'))


# Order fulfillment page
@bp.route('/sell/orders', methods=['GET', 'POST'])
def order_fulfillment_page():
    orders = Purchase.get_purchases_by_sid(current_user.id)

    # Format the datetime
    for order in orders:
        order.date_ordered = order.date_ordered.strftime("%Y-%m-%d %I:%M:%S%p")
    

    # Render Order fulfillment page
    return render_template('sell/order_fulfillment.html',
                            orders = orders)

# Toggle order fulfilled status
@bp.route('/sell/orders/<id>', methods=['GET', 'POST'])
def toggle_order_fulfilled(id):
    # Toggle
    Purchase.toggle_purchase_fulfilled(id)
    # Re-render Order page
    return redirect(url_for('sell.order_fulfillment_page'))


# Customer analytics page
@bp.route('/sell/analytics', methods=['GET', 'POST'])
def customer_analytics_page():
    
    # Average customer rating
    avg_rating = Inventory.get_avg_customer_rating(current_user.id)
    if avg_rating:
        avg_rating = round(avg_rating, 2)
    else:
        avg_rating = 'No ratings yet'
        
    # Number of customer ratings
    rating_count = Inventory.get_customer_rating_count(current_user.id)
    
    # Best-selling product
    best_selling_pid = Inventory.get_best_selling_product(current_user.id)
    # Get the product's info
    best_selling_product = Product('', 'No products purchased', '', '', '', '', '')
    if best_selling_pid:
        best_selling_product = Product.get(best_selling_pid)
    
    # Render Customer analytics page
    return render_template('sell/customer_analytics.html',
                           avg_rating = avg_rating,
                           rating_count = rating_count,
                           best_selling_product = best_selling_product)



