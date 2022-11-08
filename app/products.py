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
bp = Blueprint('product', __name__)


@bp.route('/product', methods=['GET', 'POST'])
def product_page():
    form = SearchBarForm()
    image_form = ImageUploadForm()
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


@bp.route('/product/addcart/<pid>', methods=['GET', 'POST'])
def add_to_cart(pid):
    Product.add_to_cart(pid, current_user.id)

    flash('Added to Cart')

    return redirect(url_for('index.index'))



class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')


class ImageUploadForm(FlaskForm):
    image = FileField('', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')
