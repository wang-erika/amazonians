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


    @staticmethod
    def get_all_in_cart(uid):
        rows = app.db.execute('''
SELECT uid, pid, sid, quantity, full_name, Products.name as product_name, category, image, unit_price, description
FROM Cart, Products, Users
WHERE uid = :uid AND Cart.pid = Products.id AND Users.id = Cart.sid
''',
                              uid=uid)
        return [Cart(*row) for row in rows]


    @staticmethod
    def get_total_price_in_cart(uid):
        total_price = app.db.execute('''
SELECT SUM(quantity*unit_price) AS total_value
FROM Cart, Products, Users
WHERE uid = :uid AND Cart.pid = Products.id AND Users.id = Cart.sid
''',
                              uid=uid)
        return total_price


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


    @staticmethod
    def delete_cart_item(uid, pid):
        rows = app.db.execute('''
delete from Cart
where uid = :uid and Cart.pid = :pid;
''',
                              uid=uid, 
                              pid=pid)
        
        return rows


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


    @staticmethod
    def delete_cart_item(uid, pid):
        # Delete product from Inventory
        rows = app.db.execute('''
delete from Cart
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid)
        
        return rows
    

    @staticmethod
    def delete_all_cart_items(cart):
        for item in cart:
            Cart.delete_cart_item(item.uid,item.pid)
    

    @staticmethod     
    def add_cart_to_orders(uid):
        lst = Cart.get_all_in_cart(uid)
        
        for item in lst:
            balance = app.db.execute('''
select balance
from Users 
where id = :uid
''',
                              uid=uid)
        if balance[0][0] < total:
            return False
        
        lst = Cart.get_all_in_cart(uid)
        for item in lst:
            quantity = app.db.execute('''
select quantity
from Inventory
where pid = :pid
''',
                              pid=item.pid)
            
            #todo 
            if item.quantity <= quantity[0][0] and balance >= Cart.get_total_price_in_cart(uid):
                rows = app.db.execute('''
insert into Orders(uid, fulfilled)
VALUES(:uid, :fulfilled)
returning id;
''',
                                uid=item.uid,
                                fulfilled = False)
                return 1
            else:
                flash('order could not be completed, too much quantity')

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

    @staticmethod 
    def check_balance(uid, total):
        balance = app.db.execute('''
select balance
from Users
where id = :uid;
''',
                              uid=uid)[0][0]
        
        return not (balance < total)
    
    @staticmethod
    def edit_balance_user(uid, total):
        balance = app.db.execute('''
select balance
from Users
where id = :uid;
''',
                              uid=uid)[0][0]
        User.update_balance(uid, float(balance) - total)

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
    
    @staticmethod
    def edit_quantity(cart):
        for item in cart:
            in_stock_quantity = app.db.execute('''
select quantity
from Inventory
where pid = :pid;
''',
                              pid=item.pid)[0][0]
            Inventory.edit_inventory_item(item.sid, item.pid, in_stock_quantity - item.quantity)

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
    def order_map_purchases(uid, orders):
        map = {}
        
        for order in orders:
            oid = order.id
            # Maps to a list where 1st element is list of purchases
            # and 2nd element is total price for this order
            map[order] = [
                Cart.update_dates(Cart.update_image(Purchase.get_purchases_by_oid_and_uid(oid, uid))),
                Cart.get_order_total(oid, uid)
            ]
            
            
        return map

    @staticmethod 
    def update_dates(products):
        for item in products:
            if item.time_purchased:
                item.time_purchased = item.time_purchased.strftime("%Y-%m-%d %I:%M:%S%p")
        return products

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
    
    @staticmethod
    def get_quantity(pid,uid):
        ret = app.db.execute('''
 SELECT quantity from Cart
 WHERE pid = :pid and uid=:uid
        ''', pid=pid, uid=uid)
        return ret

