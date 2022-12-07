from flask import current_app as app
from flask import flash

from app.models.purchase import Purchase
from app.models.user import User
from app.models.inventory import Inventory
from datetime import datetime

class Cart:
    def __init__(self, uid, pid, sid, quantity, full_name, product_name, category, image, unit_price, description):
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.quantity = quantity
        self.full_name = full_name
        self.product_name = product_name
        self.category = category
        self.image = image
        self.unit_price = unit_price
        self.description = description


    """
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid
FROM Cart
WHERE id = :id
''',
                              id=id)
        return Cart(*(rows[0])) if rows else None
    """

    #Given id of the user, return a list of products in their Cart (and associated info)
    @staticmethod
    def get_all_in_cart(uid):
        rows = app.db.execute('''
SELECT uid, pid, sid, quantity, full_name, Products.name as product_name, category, image, unit_price, description
FROM Cart, Products, Users
WHERE uid = :uid AND Cart.pid = Products.id AND Users.id = Cart.sid
''',
                              uid=uid)
        return [Cart(*row) for row in rows]

    #Given id of the user, return a subtotal price (Sum of quantity times unit price) of products in their Cart 
    @staticmethod
    def get_total_price_in_cart(uid):
        total_price = app.db.execute('''
SELECT SUM(quantity*unit_price) AS total_value
FROM Cart, Products, Users
WHERE uid = :uid AND Cart.pid = Products.id AND Users.id = Cart.sid
''',
                              uid=uid)
        return total_price

    #Given id of user and id of the product id, return a list of product associated info stored in the cart
    #used to when viewing a specific product to see associated info and/or make changes in quantity or delete
    @staticmethod
    def get_all_in_cart_by_pid(uid, pid):
        rows = app.db.execute('''
SELECT uid, pid, sid, quantity, full_name, Products.name as product_name, category, image, unit_price, description
from Cart, Products, Users
where uid = :uid and Cart.pid = Products.id and Cart.pid = :pid AND Users.id = Cart.sid
''',
                              uid=uid, 
                              pid=pid)
        
        return Cart(*(rows[0])) if rows is not None else None 

    #Given a id of user, and id of the product delete item/product from that user's cart
    @staticmethod
    def delete_cart_item(uid, pid):
        rows = app.db.execute('''
delete from Cart
where uid = :uid and Cart.pid = :pid;
''',
                              uid=uid, 
                              pid=pid)
        
        return rows

    #Given a id of user, id of the product, and user inputed quantity
    #Edit quantity of item in a person's cart 
    @staticmethod
    def edit_cart_item(uid, pid, quantity):
        rows = app.db.execute('''
update Cart
set quantity = :quantity
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid,
                              quantity=quantity)

        return rows

    #Given a cart class variable, deleted all cart items in the cart
    #utilizes delete_cart_item
    @staticmethod
    def delete_all_cart_items(cart):
        for item in cart:
            Cart.delete_cart_item(item.uid,item.pid)

    #Given a id of user, id of the product, id of the seller and user inputed quantity
    #add a product to the cart
    @staticmethod
    def add_product_to_cart(uid, sid, pid, quantity):
        try:
            rows = app.db.execute('''
insert into Cart(uid, sid, pid, quantity)
VALUES(:uid, :sid, :pid, :quantity)
returning uid, sid, pid
''',
                              uid=uid, sid = sid, pid=pid, quantity = quantity)
            cart_info = rows[0]
            if cart_info:
                return True
            else:
                return False

        except Exception as e:
            print(str(e))
            return False

    #Given id of user and total price of cart
    #return boolean for whether user has enough balance (balance > total)
    @staticmethod 
    def check_balance(uid, total):
        balance = app.db.execute('''
select balance
from Users
where id = :uid;
''',
                              uid=uid)[0][0]
        
        return not (balance < total)
    
    #Given id of user and total price of cart
    #edits the balance of the user (decrements the buyer's balance)
    @staticmethod
    def edit_balance_user(uid, total):
        balance = app.db.execute('''
select balance
from Users
where id = :uid;
''',
                              uid=uid)[0][0]
        User.update_balance(uid, float(balance) - total)
    
    #Given items in cart
    #edits the balance for a seller 
    #indentifies price at purchase with quantity and then increments seller's balance
    @staticmethod
    def edit_balance_seller(cart):
        for item in cart:
            balance = app.db.execute('''
select balance
from Users
where id = :uid;
''',
                              uid=item.sid)[0][0]
            #get item price
            price = app.db.execute('''
select unit_price
from Products
where id = :uid;
''',
                              uid=item.pid)[0][0]
            
            User.update_balance(item.sid, float(balance) + float(price)*item.quantity)

    #Given items in cart
    #return boolean for whether seller's has enough quantity (quantity > in_stock_quantity)
    #for all items in the cart
    @staticmethod 
    def check_quantity(cart):
        for item in cart:
            in_stock_quantity = app.db.execute('''
select quantity
from Inventory
where pid = :pid;
''',
                              pid=item.pid)[0][0]

            if item.quantity > in_stock_quantity:
                return False
        
        return True
    
    #Given items in cart
    #edits the quantity of items in a sellers' (users') inventory
    #done for all items in cart
    @staticmethod
    def edit_quantity(cart):
        for item in cart:
            in_stock_quantity = app.db.execute('''
select quantity
from Inventory
where pid = :pid;
''',
                              pid=item.pid)[0][0]
            Inventory.edit_inventory_quantity(item.sid, item.pid, in_stock_quantity - item.quantity)

    #Given uid
    #adds user's order into Orders and sets fulfilment for order to be false (default)
    @staticmethod
    def add_order_to_orders(uid):
        try:
            rows = app.db.execute('''
insert into Orders(uid, fulfilled)
VALUES(:uid, :fulfilled)
returning id;
''',
                              uid=uid,
                              fulfilled = False)
            return rows[0][0]

        except Exception as e:
            print(str(e))
            return False

    #Given cart items and order id
    #inserts cart items and relevent information into Purchases 
    @staticmethod 
    def add_items_to_purchases(cart, oid):
        for item in cart:
            rows = app.db.execute('''
insert into Purchases(oid, uid, pid, quantity, unit_price_at_time_of_payment, fulfilled)
VALUES(:oid, :uid, :pid, :quantity, :unit_price_at_time_of_payment, :fulfilled)
returning id;
''',
                              oid=oid,
                              uid=item.uid,
                              pid=item.pid,
                              quantity=item.quantity,
                              unit_price_at_time_of_payment=item.unit_price,
                              fulfilled = False)
    
    # Creates a map with key = each order id,
    # and the value is an array of purchases for that order
    # AS WELL AS the cart total for that order
    @staticmethod 
    def order_map_purchases(uid, orders, text):
        map = {}
        
        if text:
            sorted_orders = Purchase.get_oid_purchases_by_uid_and_search(uid, text)
        for order in orders:
            oid = order.id
            if text:
                if oid not in sorted_orders:
                    continue
                else:
                    # Maps to a list where 1st element is list of purchases
                    # and 2nd element is total price for this order
                    map[order] = [
                        #updates to certain elements of purchases (inner most to format images, next inner most to update dates to be formated
                        #lastly, to update seller_name to exisit and be accessible)
                        
                        Cart.update_seller_name(Cart.update_dates(Cart.update_image(Purchase.get_purchases_by_oid_and_uid(oid, uid)))),
                        Cart.get_order_total(oid, uid)
                    ]
            else:
                map[order] = [
                        #updates to certain elements of purchases (inner most to format images, next inner most to update dates to be formated
                        #lastly, to update seller_name to exisit and be accessible)
                        
                        Cart.update_seller_name(Cart.update_dates(Cart.update_image(Purchase.get_purchases_by_oid_and_uid(oid, uid)))),
                        Cart.get_order_total(oid, uid)
                    ]
        return map
    
    #Given products, updates seller's name for all products
    #returning products
    @staticmethod
    def update_seller_name(products):
        for item in products:
            if item.sid:
                item.seller_name = Cart.get_seller_name(item.sid)
        return products

    #Given products, updates dates to appear in standard format for all products
    #returning products
    @staticmethod 
    def update_dates(products):
        for item in products:
            if item.time_purchased:
                item.time_purchased = item.time_purchased.strftime("%Y-%m-%d %I:%M:%S%p")
        return products

    #Given products, updates images to appear in format for all products
    #returning products
    @staticmethod
    def update_image(products):
        for item in products:
            if (item.image.tobytes() == b'0'):
                item.image = '../../static/default.jpg'
            else:
                try:
                    item.image = '../../static/' + str(item.pid) + '.png'  
                except:
                    item.image = '../../static/' + str(item.id) + '.png'  
        return products

    #Given order id and user id
    #returns subtotal price for a select order
    @staticmethod 
    def get_order_total(oid, uid):
        rows = app.db.execute('''
SELECT SUM(Purchases.quantity * unit_price_at_time_of_payment) as total_value
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
    join Inventory
    on Purchases.pid = Inventory.pid
where Purchases.oid = :oid
    and Purchases.uid = :uid
''',    
                              oid=oid,
                              uid=uid)
        return rows[0][0]
    
    #Given product id and user id
    #return the quantity from the Cart
    @staticmethod
    def get_quantity(pid,uid):
        ret = app.db.execute('''
 SELECT quantity from Cart
 WHERE pid = :pid and uid=:uid
        ''', pid=pid, uid=uid)
        return ret
    
    #Given seller id
    #return the seller's name found from users
    @staticmethod
    def get_seller_name(sid):
        ret = app.db.execute('''
 SELECT full_name 
 from Users
 WHERE id = :sid
        ''', sid=sid)
        return ret[0][0]

