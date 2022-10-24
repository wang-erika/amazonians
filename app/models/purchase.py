from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.name = name
        self.price = price

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, time_purchased, Products.name, Products.unit_price,
FROM Purchases, Products
WHERE Purchases.id = :id, and Purchases.pid = Products.id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Products.name, Products.unit_price
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
SELECT Purchases.id, uid, pid, time_purchased, name, unit_price
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
''',    uid = uid)
        return [Purchase(*row) for row in rows]