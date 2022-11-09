from flask import current_app as app


class Purchase:
    def __init__(self, id, oid, date_ordered, uid, user_full_name, user_address, pid, product_name, category, image, description, quantity, time_purchased, unit_price_at_time_of_payment, fulfilled):
        self.id = id

        # From Orders
        self.oid = oid
        self.date_ordered = date_ordered

        # From Users
        self.uid = uid
        self.user_full_name = user_full_name
        self.user_address = user_address

        # From Products
        self.pid = pid
        self.product_name = product_name
        self.category = category
        self.image = image
        self.description = description

        # From Purchases
        self.quantity = quantity
        self.time_purchased = time_purchased
        self.unit_price_at_time_of_payment = unit_price_at_time_of_payment
        self.fulfilled = fulfilled


    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, Products.category, Products.image, Products.description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
WHERE Purchases.id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, Products.category, Products.image, Products.description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
WHERE Purchases.uid = :uid
    AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_purchases(uid):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, Products.category, Products.image, Products.description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
WHERE Purchases.uid = :uid
''',    
                              uid = uid)
        
        return [Purchase(*row) for row in rows]

    # given seller id, return all purchases associated with that seller
    # IN REVERSE CHRONOLOGICAL ORDER
    def get_purchases_by_sid(sid):
            rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, category, image, description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
    join Inventory
    on Purchases.pid = Inventory.pid
where Inventory.sid = :sid
order by Orders.date_ordered desc
''',    
                              sid=sid)
        
            return [Purchase(*row) for row in rows]

    # given purchase id, toggle fulfilled status
    @staticmethod
    def toggle_purchase_fulfilled(id):
        # Get current status
        status = app.db.execute('''
select fulfilled
from Purchases
where id = :id
''',
                              id=id)

        # toggle
        status = 'f' if (status[0][0]) else 't'

        rows = app.db.execute('''
update Purchases
set fulfilled = :fulfilled
where id = :id;
''',
                              id=id,
                              fulfilled=status)