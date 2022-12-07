from flask import current_app as app


class Product:
    def __init__(self, id, name, category, image, unit_price, description, quantity):
        self.id = id
        self.name = name
        self.category = category
        self.image = image
        self.unit_price = unit_price
        self.description = description
        self.quantity = quantity
        
    # this method gets a given product given the id
    @staticmethod
    def get(pid):
        rows = app.db.execute('''
SELECT id, name, category, image, unit_price, description, quantity
FROM Products, Inventory
WHERE pid = :pid AND Inventory.pid = Products.id
''',
                              pid=pid)
        return Product(*(rows[0])) if rows is not None else None
    
    
    # this method gets all products in inventory 
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT id, name, category, image, unit_price, description, quantity
FROM Products, Inventory
WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
ORDER BY unit_price ASC
''',
                              )
                              
        return [Product(*row) for row in rows]

    # this method gets the top k most expensive products 
    @staticmethod
    def get_top_k(k):
        rows = app.db.execute('''
SELECT id, name, category, image, unit_price, description, sum(quantity) as quantity
FROM Products, Inventory
WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
GROUP BY id
ORDER BY unit_price DESC
LIMIT :k
''', k = k)
        return [Product(*row) for row in rows]

    # this method adds the product to the cart
    @staticmethod
    def add_to_cart(pid, uid, amount):
        sid = Product.get_sid_from_pid(pid)
        cart = Product.in_cart(pid, uid)
        if not cart:
            rows = app.db.execute('''
    INSERT INTO Cart(uid, pid, sid, quantity)        
    VALUES(:uid, :pid, :sid, :quantity)''', uid=uid, pid=pid, sid=sid, quantity=amount)
        else:
            rows = app.db.execute('''
    UPDATE Cart SET quantity = quantity+:amount WHERE pid=:pid         
            ''', pid=pid, amount=amount)

    # this method helps find the seller id of the product given the product id
    @staticmethod
    def get_sid_from_pid(pid):
        sid = app.db.execute('''
SELECT sid FROM Inventory
WHERE pid=:pid''', pid=pid)
        return sid[0][0]

    # this method tells if the product is in the cart or not
    @staticmethod
    def in_cart(pid, uid):
        ret = app.db.execute(''' 
 SELECT quantity from Cart
 WHERE pid=:pid and uid=:uid      
        ''', pid=pid, uid=uid)
        return len(ret) > 0

    # this method is like get_all(), but instead queries the database with the given constraints to find all matches
    @staticmethod
    def query_amount(text="", category="", sortby=True):
        text = '%' + text.lower() + '%'
        category = '%' + category + '%'
        if sortby:
            rows = app.db.execute('''
        SELECT id, name, category, image, unit_price, description, quantity
        FROM Products, Inventory
        WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
        AND (LOWER(name) LIKE :text
        OR LOWER(description) LIKE :text)
        AND category LIKE :category
        ORDER BY unit_price ASC
            ''', text=text, category=category)
        else:
            rows = app.db.execute('''
        SELECT id, name, category, image, unit_price, description, quantity
        FROM Products, Inventory
        WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
        AND (LOWER(name) LIKE :text
        OR LOWER(description) LIKE :text)
        AND category LIKE :category
        ORDER BY unit_price DESC
            ''', text=text, category=category)
        return [Product(*row) for row in rows]


# this method helps find the seller id of the product given the product id
    @staticmethod
    def get_sid_from_pid(pid):
        sid = app.db.execute('''
SELECT sid FROM Inventory
WHERE pid=:pid''', pid=pid)
        return sid[0][0]


 # Get the seller name from the pid
    @staticmethod
    def get_seller_name_from_pid(pid):
        rows = app.db.execute('''
SELECT Users.full_name
FROM Sellers, Users, Inventory
WHERE Inventory.pid = :pid
AND Inventory.sid = Sellers.id
AND Sellers.id = Users.id
''',
                              pid = pid)
        return rows[0][0]
