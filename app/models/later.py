from flask import current_app as app
from flask import flash

from app.models.purchase import Purchase
from app.models.user import User
from app.models.inventory import Inventory

class Later:
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
    
    #Given id of the user, return a list of products in their saved for later (and associated info)
    @staticmethod
    def get_all_in_saved_for_later(uid):
        rows = app.db.execute('''
SELECT uid, pid, sid, quantity, full_name, Products.name as product_name, category, image, unit_price, description
FROM Later, Products, Users
WHERE uid = :uid AND Later.pid = Products.id AND Users.id = Later.sid
''',
                              uid=uid)
        return [Later(*row) for row in rows]
    
    #Given id of user and id of the product id, return a list of product associated info stored in the saved for later
    #used to when viewing a specific product to see associated info and/or make changes in quantity or delete
    @staticmethod
    def get_all_in_later_by_pid(uid, pid):
        rows = app.db.execute('''
SELECT uid, pid, sid, quantity, full_name, Products.name as product_name, category, image, unit_price, description
from Later, Products, Users
where uid = :uid and Later.pid = Products.id and Later.pid = :pid AND Users.id = Later.sid
''',
                              uid=uid, 
                              pid=pid)
        
        return Later(*(rows[0])) if rows is not None else None 
    
    #Given a id of user, id of the product, id of the seller and user inputed quantity
    #add/move a product to the saved for later
    @staticmethod
    def add_into_saved_for_later(uid, sid, pid, quantity):
        rows = app.db.execute('''
insert into Later(uid, sid, pid, quantity)
VALUES(:uid, :sid, :pid, :quantity)
returning uid, sid, pid
''',
                              uid=uid, sid=sid, pid=pid, quantity=quantity)
        return rows
    
    #Given a id of user, and id of the product delete item/product from that user's saved for later
    @staticmethod
    def delete_later_item(uid, pid):
        rows = app.db.execute('''
delete from Later
where uid = :uid and Later.pid = :pid;
''',
                              uid=uid, 
                              pid=pid)
        
        return rows
    
    #Given a id of user, id of the product, and user inputed quantity
    #Edit quantity of item in a person's saved for later 
    @staticmethod
    def edit_later_item(uid, pid, quantity):
        rows = app.db.execute('''
update Later
set quantity = :quantity
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid,
                              quantity=quantity)

        return rows
    
    #Given id of user and the id of the product
    #Return the quantity for that specific product in Later
    @staticmethod
    def get_later_quantity(pid,uid):
        ret = app.db.execute('''
 SELECT quantity from Later
 WHERE pid = :pid and uid=:uid
        ''', pid=pid, uid=uid)
        return ret
    
    #Given id of user and id of the product
    #Delete that item from the Later table
    @staticmethod
    def delete_later_item(uid, pid):
        # Delete product from Inventory
        rows = app.db.execute('''
delete from Later
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid)
        
        return rows
    