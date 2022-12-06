from flask import current_app as app
from flask import flash


class Purchase:
    def __init__(self, id, oid, date_ordered, uid, user_full_name, user_address, pid, product_name, category, image, description, quantity, time_purchased, unit_price_at_time_of_payment, fulfilled, sid, seller_name):
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
        
        # FROM Inventory
        self.sid = sid
        self.seller_name = seller_name


    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, Products.category, Products.image, Products.description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled, sid, null AS seller_name
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
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, Products.category, Products.image, Products.description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled, sid, null AS seller_name
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
    join Inventory
    on Purchases.pid = Inventory.pid
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
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, Products.category, Products.image, Products.description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled, sid, null AS seller_name
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
    join Inventory
    on Purchases.pid = Inventory.pid
WHERE Purchases.uid = :uid
ORDER BY time_purchased DESC
''',    
                              uid = uid)
        
        return [Purchase(*row) for row in rows]

    # given seller id, return all purchases associated with that seller
    # IN REVERSE CHRONOLOGICAL ORDER
    def get_purchases_by_sid(sid):
            rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, category, image, description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled, sid, null AS seller_name
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
        
    @staticmethod
    def get_purchases_by_oid(oid, uid):
            rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, category, image, description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled, sid, null AS seller_name
FROM Purchases join Orders
    on Purchases.oid = Orders.id
    join Users
    on Purchases.uid = Users.id
    join Products
    on Purchases.pid = Products.id
    join Inventory
    on Purchases.pid = Inventory.pid
WHERE oid = :oid
''',    
                              oid=oid,
                              uid=uid)
            return [Purchase(*row) for row in rows]

    # given purchase id, check current status
    @staticmethod 
    def check_purchase_fulfillment(id):
        status = app.db.execute('''
select fulfilled
from Purchases
where id = :id
''',
                              id=id)
        return status

    # given purchase id, toggle fulfilled status
    @staticmethod
    def toggle_purchase_fulfilled(id):
        # Get current status
        status = Purchase.check_purchase_fulfillment(id)

        # toggle
        status = 'f' if (status[0][0]) else 't'

        rows = app.db.execute('''
update Purchases
set fulfilled = :fulfilled
where id = :id;
''',
                              id=id,
                              fulfilled=status)
        
        # after the update, get the order id
        oid = Purchase.get_order_id(id)
        
        # check to see if order id fulfilled status can be updated
        if Purchase.is_fulfilled(oid):
            # Update fulfilled status to true
            Purchase.update_order_fulfillment(oid, 't')
        else:
            # Update fulfilled status to false
            Purchase.update_order_fulfillment(oid, 'f')
    
    # given purchase id, find order id
    @staticmethod 
    def get_order_id(purchase_id):
        rows = app.db.execute('''
select oid
from Purchases
where id = :id
''',
                              id=purchase_id)
        return rows[0][0]
    
    # given order id, check to see if any purchases are still unfulfilled
    @staticmethod 
    def is_fulfilled(oid):        
        rows = app.db.execute('''
select count(*)
from Purchases
where oid = :oid and fulfilled = 'f'
''',
                              oid=oid)
        
        # If count == 0, then order is fulfilled
        return True if rows[0][0] == 0 else False
        
    # given order id, update its fulfillment status
    def update_order_fulfillment(oid, status):        
        rows = app.db.execute('''
update Orders
set fulfilled = :fulfilled
where id = :id;
''',
                              id=oid,
                              fulfilled=status)        


    # given order id and a given user
    # return purchases
    def get_purchases_by_oid_and_uid(oid, uid):
            rows = app.db.execute('''
SELECT Purchases.id, Purchases.oid, Orders.date_ordered, Purchases.uid, Users.full_name as user_full_name, Users.address as user_address, Purchases.pid, Products.name as product_name, category, image, description, Purchases.quantity, time_purchased, unit_price_at_time_of_payment, Purchases.fulfilled, sid, null AS seller_name
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
        
            return [Purchase(*row) for row in rows]