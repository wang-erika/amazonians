from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed 
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
import sys
from app.models.inventory import Inventory

from app.models.review import Review

from .models.product import Product

from flask import Blueprint
bp = Blueprint('product', __name__)


# @bp.route('/product', methods=['GET', 'POST'])
# def k_product_page():
#     form = SearchBarForm()
#     image_form = ImageUploadForm()
#     # if query submitted
#     product = []
#     if form.validate_on_submit():
#         print(form.query, file=sys.stderr)
        
#         product = Product.get_top_k(form.query.data)
#         #cart = Cart.get_all_in_cart_by_pid(current_user.id, form.query.data)
        
#         if not product:
#             product = []

#         return render_template('product.html',
#                             product = product, form = form)

#     # default: render full cart
#     return render_template('product.html', 
#                             product = product, form = form)


#individual product page
@bp.route('/product/<pid>', methods = ['GET', 'POST'])
def product_page(pid):
    stats = Review.get_product_stats(pid)
    num_reviews = Review.get_number_ratings(pid)
    prod = Product.get(pid)
    stock = Inventory.get_product_quantity(pid)
    add_cart_form = AddToCartForm()
    summary_reviews = Review.get_summary_reviews(pid)
    if (prod.image.tobytes() == b'0'):
        prod.image = '../../static/default.jpg'
    else:
        prod.image = '../../static/' + str(prod.id) + '.png'

    if add_cart_form.validate_on_submit():
        Product.add_to_cart(prod.id, current_user.id, add_cart_form.quantity.data)
        flash('Added to Cart')
        return redirect(url_for('index.index'))

    return render_template('product_page.html', 
                            item = prod, 
                            stats=stats, 
                            add_cart_form=add_cart_form,
                            num_reviews = num_reviews,
                            summary_reviews = summary_reviews,
                            stock = stock)

class SearchBarForm(FlaskForm):
    query = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')


class ImageUploadForm(FlaskForm):
    image = FileField('', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Add to Cart', validators=[])
    submit = SubmitField('Add to Cart')