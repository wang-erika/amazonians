from flask import current_app as app


class Product:
    def __init__(self, id, image, category, name, unit_price, quantity, description):
        self.id = id
        self.image = image
        self.category = category
        self.name = name
        self.unit_price = unit_price
        self.quantity = quantity
        self.description = description
    """
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None
    """
    
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT id, image, category, name, unit_price, quantity, description
FROM Products, Inventory
WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
''',
                              )
        return [Product(*row) for row in rows]

        
    @staticmethod
    def get_top_k(k):
        rows = app.db.execute('''
SELECT id, image, category, name, unit_price, sum(quantity) as quantity, description
FROM Products, Inventory
WHERE Inventory.pid = Products.id AND Inventory.quantity > 0
GROUP BY id
ORDER BY unit_price DESC
LIMIT :k
''', k = k)
        return [Product(*row) for row in rows]
