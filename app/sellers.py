from flask import render_template
from flask_login import current_user

from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/sell', methods=['GET'])
def get_inventory_products():
    if current_user.is_authenticated:
        # get all products they are selling
        inventory = Inventory.get_by_sid(current_user.id)
    else:
        inventory = None

    # render Sell page (shows inventory)
    return render_template(inventory = inventory)
    
