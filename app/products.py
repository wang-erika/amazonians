from flask import render_template, flash, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed 
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models.inventory import Inventory

from app.models.review import Review

from .models.product import Product

from flask import Blueprint
bp = Blueprint('product', __name__)

 #individual product page, which is the page shown from the main page
@bp.route('/product/<pid>', methods = ['GET', 'POST'])
def product_page(pid):
    # get the stats of the product
    stats = Review.get_product_stats(pid)
    num_reviews = Review.get_number_ratings(pid)

    # get more product information 
    prod = Product.get(pid)
    stock = Inventory.get_product_quantity(pid)

    # the form needed to add the product to the cart (how many too)
    add_cart_form = AddToCartForm()
    summary_reviews = Review.get_summary_reviews(pid)

    # image processing
    if (prod.image.tobytes() == b'0'):
        prod.image = '../../static/default.jpg'
    else:
        prod.image = '../../static/' + str(prod.id) + '.png'

    # if submitted add x amount of the product to the cart
    if add_cart_form.validate_on_submit():
        Product.add_to_cart(prod.id, current_user.id, add_cart_form.quantity.data)
        flash('Added to Cart')
        # go to the main page
        return redirect(url_for('index.index'))

    # render product page
    return render_template('product_page.html', 
                            item = prod, 
                            stats=stats, 
                            add_cart_form=add_cart_form,
                            num_reviews = num_reviews,
                            summary_reviews = summary_reviews,
                            stock = stock)

# form for adding to the cart and how much to add
class AddToCartForm(FlaskForm):
    quantity = IntegerField('Add to Cart', validators=[])
    submit = SubmitField('Add to Cart')