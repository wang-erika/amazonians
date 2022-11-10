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

    return render_template('reviews/temp.html', 
                            product_reviews = product_reviews, 
                            seller_reviews = seller_reviews)

# create product review form
class AddProductReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators = [DataRequired()])
    review = StringField("Review", validators = [])
    submit = SubmitField('Post Review')

# create seller review form
class AddSellerReviewForm(FlaskForm):
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
    
    if not Review.user_purchased_product(current_user.id, pid):
        flash('You have not purchased this product')
        return redirect(url_for('reviews.reviews_page'))

    # Create form
    add_form = AddProductReviewForm()

    # Redirect to main Sell page once form completed
    if add_form.validate_on_submit():
        if add_form.rating.data > 5 or add_form.rating.data < 1:
            flash('Please Enter a Number Between 1-5')
            return redirect(url_for('reviews.add_product_review', pid = pid))


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


# add new seller review for the user
@bp.route('/reviews/seller/<sid>', methods=['GET', 'POST'])
def add_seller_review(sid):

    # if there already is a product review
    if Seller_Review.has_seller_review(current_user.id, sid):
        flash('You already have a review for this seller')
        return redirect(url_for('reviews.reviews_page'))

    if not Seller_Review.user_purchased_seller(current_user.id, sid):
        flash('You have not purchased a product from this seller')
        return redirect(url_for('reviews.reviews_page'))
    

    # Create form
    add_form = AddSellerReviewForm()

    # Redirect to main Sell page once form completed
    if add_form.validate_on_submit():
        if add_form.rating.data > 5 or add_form.rating.data < 1:
            flash('Please Enter a Number Between 1-5')
            return redirect(url_for('reviews.add_seller_review', sid = sid))


        Seller_Review.add_new_seller_review(current_user.id,
                                    sid,
                                    datetime.now(),
                                    add_form.rating.data,
                                    add_form.review.data)
            
            # Success message
        msg = 'Success! Review Added.'
        flash(msg)
            
        return redirect(url_for('reviews.reviews_page'))

    # Render Add page with form
    return render_template('reviews/write_seller_review.html',
                            add_form = add_form, 
                            seller = sid)


# delete a product review
@bp.route('/reviews/delete/<pid>', methods=['GET', 'POST'])
def delete_product_review(pid):
    # Delete product from database
    Review.delete_product_review(current_user.id, pid)

    # Success message
    flash('Review deleted.')

    # Re-render Sell page
    return redirect(url_for('reviews.reviews_page'))

#delete seller review
@bp.route('/reviews/seller/delete/<sid>', methods=['GET', 'POST'])
def delete_sr(sid):
    # Delete seller review from database
    Seller_Review.delete_seller_review(current_user.id, sid)

    # Success message
    flash('Review deleted.')

    # Re-render Sell page
    return redirect(url_for('reviews.reviews_page'))


# Details page -- view a review's details
@bp.route('/reviews/detail/<pid>', methods=['GET', 'POST'])
def view_product_review(pid):
    # Create edit form
    edit_form = EditProductReviewForm()

    # Get Review Details
    review = Review.get_product_review(current_user.id, pid)

    # Re-render page if edit form is submitted
    if edit_form.validate_on_submit():
        if edit_form.rating.data > 5 or edit_form.rating.data < 1:
            flash('Please Enter a Number Between 1-5')
            return redirect(url_for('reviews.view_product_review', pid = pid))
            
        Review.delete_product_review(current_user.id, pid)
        Review.add_new_product_review(current_user.id,
                                    pid,
                                    datetime.now(),
                                    edit_form.rating.data,
                                    edit_form.review.data)
        
        msg = 'Review Updated'
        flash(msg)
        return redirect(url_for('reviews.reviews_page'))

    # Render Details page
    return render_template('reviews/review_details.html',
                            review= review,
                            edit_form = edit_form)

class EditProductReviewForm(FlaskForm):
    rating = IntegerField('New Rating', validators = [DataRequired()])
    review = StringField("New Review", validators = [])
    submit = SubmitField('Update')


# Details page -- view a review's details
@bp.route('/reviews/seller/edit/<sid>', methods=['GET', 'POST'])
def view_seller_review(sid):
    # Create edit form
    edit_form = EditSellerReviewForm()

    # Get Review Details
    seller_review = Seller_Review.get_seller_review(current_user.id, sid)

    # Re-render page if edit form is submitted
    if edit_form.validate_on_submit():
        if edit_form.rating.data > 5 or edit_form.rating.data < 1:
            flash('Please Enter a Number Between 1-5')
            return redirect(url_for('reviews.view_seller_review', sid = sid))
            
        Seller_Review.delete_seller_review(current_user.id, sid)
        Seller_Review.add_new_seller_review(current_user.id,
                                    sid,
                                    datetime.now(),
                                    edit_form.rating.data,
                                    edit_form.review.data)
        
        msg = 'Review Updated'
        flash(msg)
        return redirect(url_for('reviews.reviews_page'))

    # Render Details page
    return render_template('reviews/seller_review_details.html',
                            review = seller_review,
                            edit_form = edit_form)

class EditSellerReviewForm(FlaskForm):
    rating = IntegerField('New Rating', validators = [DataRequired()])
    review = StringField("New Review", validators = [])
    submit = SubmitField('Update')

