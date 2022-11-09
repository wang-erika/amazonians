from flask import current_app as app
from flask import flash

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
            
            quantity = app.db.execute('''
select quantity
from Inventory
where pid = :pid
''',
                              pid=item.pid)
            
            #todo 
            if item.quantity <= quantity[0][0] and balance >= Cart.get_total_price_in_cart(uid):
                rows = app.db.execute('''
insert into Orders(uid, sid, pid, quantity, fulfilled, unit_price_at_time_of_payment)
VALUES(:uid, :sid, :pid, :quantity, :fulfilled, :unit_price_at_time_of_payment)
returning uid, sid, pid, quantity, fulfilled, unit_price_at_time_of_payment
''',
                                uid=item.uid, sid = item.sid, pid=item.pid, quantity = item.quantity, fulfilled = False, 
                                unit_price_at_time_of_payment = item.unit_price,
                                )
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
