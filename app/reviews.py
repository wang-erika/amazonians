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
from datetime import datetime
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
bp = Blueprint('reviews', __name__)


# shows product and seller reviews of that user
@bp.route('/reviews', methods = ['GET', 'POST'])
def reviews_page():

    product_reviews = Review.get_all_product_reviews(current_user.id)
    seller_reviews = Seller_Review.get_all_seller_reviews(current_user.id)

    return render_template('reviews/your_reviews.html', 
                            product_reviews = product_reviews, 
                            seller_reviews = seller_reviews)

# create product review form
class AddProductReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators = [DataRequired()])
    review = StringField("Review", validators = [])
    submit = SubmitField('Post Review')


# add new product review for the user
@bp.route('/reviews/<pid>', methods=['GET', 'POST'])
def add_product_review(pid):

    # if there already is a product review
    if Review.has_product_review(current_user.id, pid):
        flash('You have already reviews for this product')
        return redirect(url_for('reviews.reviews_page'))

    # Create form
    add_form = AddProductReviewForm()

    # Redirect to main Sell page once form completed
    if add_form.validate_on_submit():
        Review.add_new_product_review(current_user.id,
                                    pid,
                                    datetime.now(),
                                    add_form.rating.data,
                                    add_form.review.data)
            
            # Success message
        msg = 'Success! Review Added.'
        flash(msg)
            
        return redirect(url_for('reviews.reviews_page'))

    # Render Add page with form
    return render_template('reviews/write_product_review.html',
                            add_form = add_form)


# delete a product review
@bp.route('/reviews/delete/<pid>', methods=['GET', 'POST'])
def delete_product_review(pid):
    # Delete product from database
    Review.delete_product_review(current_user.id, pid)

    # Success message
    flash('Review deleted.')

    # Re-render Sell page
    return redirect(url_for('reviews.reviews_page'))

# edit a product review'''

