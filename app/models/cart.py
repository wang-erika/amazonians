from flask import current_app as app


class Cart:
    """
    This is just a TEMPLATE for Cart, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, uid, product_name, pid, sid, quantity, unit_price):
        self.uid = uid
        self.product_name = product_name
        self.pid = pid
        self.sid = sid 
        self.quantity = quantity
        self.unit_price = unit_price

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
SELECT uid, name, pid, sid, quantity, unit_price
FROM Cart, Products
WHERE uid = :uid AND Cart.pid = Products.id
''',
                              uid=uid)
        return [Cart(*row) for row in rows]

    @staticmethod
    def get_all_in_cart_by_pid(uid, pid):
        rows = app.db.execute('''
select uid, name, pid, sid, quantity, unit_price
from Cart, Products
where uid = :uid and Cart.pid = Products.id and Cart.pid = :pid
''',
                              uid=uid, pid=pid)

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