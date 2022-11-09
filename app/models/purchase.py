from flask import current_app as app


class Purchase:
    def __init__(self, id, oid, uid, pid, product_name, quantity, time_purchased, unit_price_at_time_of_payment, fulfilled):
        self.id = id
        self.oid = oid
        self.uid = uid
        self.pid = pid
        self.product_name = product_name
        self.quantity = quantity
        self.time_purchased = time_purchased
        self.unit_price_at_time_of_payment = unit_price_at_time_of_payment
        self.fulfilled = fulfilled


    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Purchases.uid, Purchases.pid, Products.name as product_name, time_purchased, unit_price_at_time_of_payment, fulfilled
FROM Purchases, Products
WHERE Purchases.id = :id, and Purchases.pid = Products.id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Purchases.uid, Purchases.pid, Products.name as product_name, time_purchased, unit_price_at_time_of_payment, fulfilled
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_purchases(uid):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Purchases.uid, Purchases.pid, Products.name as product_name, time_purchased, unit_price_at_time_of_payment, fulfilled
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
''',    
                              uid = uid)
        
        return [Purchase(*row) for row in rows]