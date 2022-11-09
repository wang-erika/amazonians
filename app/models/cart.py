from flask import current_app as app
from flask import flash

from app.models.purchase import Purchase
from app.models.order import Order

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
    def delete_all_cart_items(uid):
        lst = Cart.get_all_in_cart(uid)
        for item in lst:
            Cart.delete_cart_item(uid,item.pid)
            
    #boolean checker for inventory and balance
    @staticmethod
    def submit_order_check(uid, total):
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
            if item.quantity >= quantity[0][0]:
                return False
        return True
    
    @staticmethod
    def add_order_to_orders(uid, total):
        if Cart.submit_order_check(uid, total):
            rows = app.db.execute('''
insert into Orders(uid, fulfilled)
VALUES(:uid, :fulfilled)
returning uid, fulfilled
''',
                              uid=uid, fulfilled = False)
            oid = app.db.execute('''
SELECT id
FROM Orders 
ORDER BY ID DESC LIMIT 1
                                 ''')[0][0]
            return oid
        else:
            flash("You either don't have enough funds or there is not enough quantity")
            return False
        
    @staticmethod
    def add_items_to_purchases(uid, oid):
        lst = Cart.get_all_in_cart(uid)
        for item in lst:
            rows = app.db.execute('''
insert into Purchases(oid, uid, pid, quantity, unit_price_at_time_of_payment, fulfilled)
VALUES(:oid, :uid, :pid, :quantity, :unit_price_at_time_of_payment, :fulfilled)
returning oid, uid, pid, quantity, unit_price_at_time_of_payment, fulfilled
''',
                              oid = oid,
                              uid=uid, 
                              pid = item.pid,
                              quantity = item.quantity, 
                              unit_price_at_time_of_payment = item.unit_price,
                              fulfilled = False
                              )
    
    @staticmethod
    def order_map_purchases(uid):
        map = {}
        orders = Order.get_orders_by_uid(uid)
        for items in orders:
            oid = items.id
            map[items] = [Purchase.get_purchases_by_oid(oid, uid), Cart.get_total_cart_amount(uid, oid)]
        return map

    @staticmethod
    def get_total_cart_amount(uid, oid):
        total = app.db.execute('''
SELECT SUM(Purchases.quantity*unit_price_at_time_of_payment) AS total_value
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
    join Inventory
    on Purchases.pid = Inventory.pid
WHERE oid = :oid and users.id = :uid
''',    
                              oid=oid, uid = uid)
        return total[0][0]

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
