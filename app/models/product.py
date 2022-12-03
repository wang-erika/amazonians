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
        
    
    @staticmethod
    def get(pid):
        rows = app.db.execute('''
SELECT id, name, category, image, unit_price, description, quantity
FROM Products, Inventory
WHERE pid = :pid AND Inventory.pid = Products.id
''',
                              pid=pid)
        return Product(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT id, name, category, image, unit_price, description, quantity
FROM Products, Inventory
WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
''',
                              )
                              
        return [Product(*row) for row in rows]

        
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


    @staticmethod
    def add_to_cart(pid, uid):
        sid = Product.get_sid_from_pid(pid)
        cart = Product.in_cart(pid, uid)
        if not cart:
            rows = app.db.execute('''
    INSERT INTO Cart(uid, pid, sid, quantity)        
    VALUES(:uid, :pid, :sid, 1)''', uid=uid, pid=pid, sid=sid)
        else:
            rows = app.db.execute('''
    UPDATE Cart SET quantity = quantity+1 WHERE pid=:pid         
            ''', pid=pid)

    @staticmethod
    def get_sid_from_pid(pid):
        sid = app.db.execute('''
SELECT sid FROM Inventory
WHERE pid=:pid''', pid=pid)
        return sid[0][0]


    @staticmethod
    def in_cart(pid, uid):
        ret = app.db.execute(''' 
 SELECT quantity from Cart
 WHERE pid=:pid and uid=:uid      
        ''', pid=pid, uid=uid)
        return len(ret) > 0
