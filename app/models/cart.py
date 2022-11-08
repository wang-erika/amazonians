from flask import current_app as app

class Cart:
    """
    This is just a TEMPLATE for Cart, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, uid, product_name, pid, sid, quantity, unit_price, category, description, image, full_name):
        self.uid = uid
        self.product_name = product_name
        self.pid = pid
        self.sid = sid 
        self.quantity = quantity
        self.unit_price = unit_price
        self.category = category
        self.description = description
        self.image = image
        self.full_name = full_name

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
SELECT uid, name, pid, sid, quantity, unit_price, category, description, image, full_name
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
select uid, name, pid, sid, quantity, unit_price, category, description, image, full_name
from Cart, Products, Users
where uid = :uid and Cart.pid = Products.id and Cart.pid = :pid AND Users.id = Cart.sid
''',
                              uid=uid, pid=pid)
        return Cart(*(rows[0])) if rows is not None else None 
        
    @staticmethod
    def delete_cart_item(uid, pid):
        rows = app.db.execute('''
delete from Cart
where uid = :uid and Cart.pid = :pid;
''',
                              uid=uid, pid=pid)
        
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
    
    @staticmethod
    def delete_cart_item(uid, pid):
        # Delete product from Inventory
        rows = app.db.execute('''
delete from Cart
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid)
    
    @staticmethod
    def delete_all_cart_items(uid):
        lst = Cart.get_all_in_cart(uid)
        for item in lst:
            Cart.delete_cart_item(uid,item.pid)
    
    @staticmethod     
    def add_cart_to_orders(uid):
        lst = Cart.get_all_in_cart(uid)
        for item in lst:
            rows = app.db.execute('''
insert into Orders(uid, sid, pid, quantity, fulfilled, unit_price_at_time_of_payment)
VALUES(:uid, :sid, :pid, :quantity, :fulfilled, :unit_price_at_time_of_payment)
returning uid, sid, pid, quantity, fulfilled, unit_price_at_time_of_payment
''',
                              uid=item.uid, sid = item.sid, pid=item.pid, quantity = item.quantity, fulfilled = False, 
                              unit_price_at_time_of_payment = item.unit_price,
                              )

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
        except Expection as e:
            print(str(e))
            return False
