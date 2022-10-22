from flask import render_template
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all()
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases)

@bp.route('/sell', methods=['GET', 'POST'])
def inventory_page():
    if current_user.is_authenticated:
        # get all products they are selling
        inventory = Inventory.get_by_sid(current_user.id)
    else:
        inventory = None

    # render Sell page (shows inventory)
    return render_template('inventory.html', 
                            inventory = inventory)

@bp.route('/cart', methods=['GET', 'POST'])
def cart_page():
    form = SearchBarForm()
    if current_user.is_authenticated:
        # get all products they are selling
        cart = Cart.get_all_in_cart(current_user.id)
    else:
        cart = None

    # render Sell page (shows inventory)
    return render_template('cart.html', 
                            cart = cart, form = form)

class SearchBarForm(FlaskForm):
    query = StringField('query', validators=[DataRequired()])
    submit = SubmitField('search')

