from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
import sys

from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.cart import Cart
from .models.review import Review
from .models.review import Seller_Review

from flask import Blueprint
bp = Blueprint('sell', __name__)

@bp.route('/sell', methods=['GET', 'POST'])
def inventory_page():
    # form = SearchBarForm()
    add_form = AddProductToInventoryForm()

    if current_user.is_authenticated:
        # get all products they are selling
        inventory = Inventory.get_by_sid(current_user.id)
    else:
        inventory = None

    if add_form.validate_on_submit():
        if Inventory.insert_new_inventory(current_user.id,
                                    add_form.image.data,
                                    add_form.category.data,
                                    add_form.name.data,
                                    add_form.quantity.data,
                                    add_form.unit_price.data,
                                    add_form.description.data):
            flash('Product added to Products!')
            return redirect(url_for('sell.inventory_page'))
    
    # render the search query if there is one
    query_inventory = []
    # if form.validate_on_submit():
    #     query_inventory = Inventory.get_by_sid(form.query.data)
    
    # render Sell page (shows inventory)
    return render_template('inventory.html', 
                            inventory = inventory,
                            query_inventory = query_inventory,
                            # form = form,
                            add_form = add_form)

class AddProductToInventoryForm(FlaskForm):
    name = StringField('Product name', validators=[])
    category = StringField('Category', validators=[])
    description = StringField('Description', validators=[])
    unit_price = DecimalField('Unit price', validators=[])
    quantity = IntegerField('Quantity in stock', validators=[])
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Create and add')

@bp.route('/sell/add', methods=['GET', 'POST'])
def add_to_inventory_page():
    add_form = AddProductToInventoryForm()
    print("here")
    if add_form.validate_on_submit():
       # print(add_form.image.data)
        if Inventory.insert_new_inventory(current_user.id,
                                    add_form.image.data,
                                    add_form.category.data,
                                    add_form.name.data,
                                    add_form.quantity.data,
                                    add_form.unit_price.data,
                                    add_form.description.data):
            flash('Success! Product added to your inventory.')
            return redirect(url_for('sell.inventory_page'))

    return render_template('sell/add_to_inventory.html', 
                            add_form = add_form)

@bp.route('/sell/delete/<pid>', methods=['GET', 'POST'])
def delete_from_inventory(pid):
    Inventory.delete_from_inventory(current_user.id, pid)
    flash('Product removed from your inventory.')
    return redirect(url_for('sell.inventory_page'))
