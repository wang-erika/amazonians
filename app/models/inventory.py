import os
from flask import current_app as app
from werkzeug.utils import secure_filename


class Inventory:
    def __init__(self, sid, pid, name, category, image, unit_price, description, quantity):
        self.sid = sid
        self.pid = pid
        self.name = name
        self.category = category
        self.image = image
        self.unit_price = unit_price
        self.description = description
        self.quantity = quantity


    # Given id of seller, return list of products in their inventory (and associated info)
    @staticmethod
    def get_by_sid(sid):
        rows = app.db.execute('''
select sid, pid, name, category, image, unit_price, description, quantity
from Inventory join Products
    on Inventory.pid = Products.id
where sid = :sid
''',
                              sid=sid)

        return [Inventory(*row) for row in rows]


    # Given seller id and product id, 
    # return details on 1 product
    @staticmethod
    def get_by_sid_and_pid(sid, pid):
        rows = app.db.execute('''
select sid, pid, name, category, image, unit_price, description, quantity
from Inventory join Products
    on Inventory.pid = Products.id
where sid = :sid and pid = :pid
''',
                              sid=sid,
                              pid=pid)

        return Inventory(*(rows[0])) if rows is not None else None


    # PRIVATE HELPER METHOD
    # Given product details
    # insert into Products table
    # and return the created pid
    @staticmethod
    def insert_new_product(name, category, image, unit_price, description):
        try:
            rows = app.db.execute("""
INSERT INTO Products(name, category, image, unit_price, description)
VALUES(:name, :category, :image, :unit_price, :description)
RETURNING id;
""",
                                  name=name,
                                  category=category,
                                  image=image,
                                  unit_price=unit_price,
                                  description=description)
            
            pid = rows[0][0]
            return pid

        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def get_product_quantity(pid):
        rows = app.db.execute("""
            SELECT quantity 
            FROM Inventory
            WHERE pid = :pid
            """, pid = pid)
        return rows[0][0] if rows is not None else 0

    # PRIVATE HELPER METHOD
    # Given user id,
    # insert this person into the Sellers table
    @staticmethod
    def insert_new_seller(id):
        try:
            rows = app.db.execute("""
INSERT INTO Sellers(id)
VALUES(:id)
RETURNING id;
""",
                                  id=id)
            
            sid = rows[0][0]
            return sid

        except Exception as e:
            print(str(e))
            return None

    # Given seller id AND product details
    # insert into Products table
    # insert into Sellers table
    # insert into Inventory table
    # Returns created pid
    @staticmethod
    def add_new_inventory_item(sid, name, image, category, unit_price, description, quantity):
        # insert into Products
        pid = Inventory.insert_new_product(name, category, image.read(), unit_price, description)

        # stop if the Product insert did not work
        if not pid:
            return None

        # insert into Sellers (in case this person is not yet a seller)
        Inventory.insert_new_seller(sid)
            
        # then connect this product into Inventory
        try:
            rows = app.db.execute("""
INSERT INTO Inventory(sid, pid, quantity)
VALUES(:sid, :pid, :quantity)
RETURNING sid, pid;
""",
                                sid=sid,
                                pid=pid,
                                quantity=quantity)
            pid = rows[0][1]
            return pid

        except Exception as e:
            print(str(e))
            return None


    # Given sid and pid, edit product quantity
    @staticmethod
    def edit_inventory_item(sid, pid, quantity):
        rows = app.db.execute('''
update Inventory
set quantity = :quantity
where sid = :sid and pid = :pid;
''',
                              sid=sid,
                              pid=pid,
                              quantity=quantity)
        
        return rows


    # PRIVATE HELPER METHOD
    # Given product id, delete product from Products
    @staticmethod
    def delete_product(pid):
        rows = app.db.execute('''
delete from Products
where id = :pid;
''',
                              pid=pid)
        
        return rows

    # PRIVATE HELPER METHOD 
    # Given seller id, delete person from Sellers
    @staticmethod
    def delete_seller(sid):
        rows = app.db.execute('''
delete from Sellers
where id = :sid;
''',
                              sid=sid)
        
        return rows

    # Given sid and pid, delete product from inventory
    @staticmethod
    def delete_inventory_item(sid, pid):
        # Delete product from Inventory
        rows = app.db.execute('''
delete from Inventory
where sid = :sid and pid = :pid;
''',
                              sid=sid,
                              pid=pid)

        # Then delete product from Products
        Inventory.delete_product(pid)
        
        # If this seller is now no longer selling ANY products, delete them from Sellers
        if (len(Inventory.get_by_sid(sid)) == 0):
            Inventory.delete_seller(sid)
            
            
    # Given sid, get average customer rating
    @staticmethod
    def get_avg_customer_rating(sid):
        rows = app.db.execute('''
select avg(rating)
from RatesSeller
where sid = :sid;
''',
                              sid=sid)

        return rows[0][0]
    
    # Given sid, get customer rating count
    @staticmethod
    def get_customer_rating_count(sid):
        rows = app.db.execute('''
select count(*)
from RatesSeller
where sid = :sid;
''',
                              sid=sid)

        return rows[0][0]
    
    # Given sid, get best-selling product
    @staticmethod
    def get_best_selling_product(sid):
        rows = app.db.execute('''
select pid, count(*)
from Purchases natural join Inventory
where sid = :sid
group by pid
order by count desc;
''',
                              sid=sid)

        return rows[0][0] if rows else None
