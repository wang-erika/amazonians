from flask import current_app as app


class Inventory:
    def __init__(self, sid, pid, name, quantity, unit_price, description):
        self.sid = sid
        self.pid = pid
        self.name = name
        self.quantity = quantity
        self.unit_price = unit_price
        self.description = description


    # get a single inventory tuple
#     @staticmethod
#     def get(sid, pid):
#         rows = app.db.execute('''
# SELECT sid, pid, quantity
# FROM Inventory
# WHERE pid = :pid AND sid = :sid
# ''',
#                               pid=pid,
#                               sid=sid)
#         return Inventory(*(rows[0])) if rows else None

    # given id of seller, return list of products in their inventory (and associated info)
    @staticmethod
    def get_by_sid(sid):
        rows = app.db.execute('''
select sid, pid, name, quantity, unit_price, description
from Inventory join Products
    on Inventory.pid = Products.id
where sid = :sid
''',
                              sid=sid)
        return [Inventory(*row) for row in rows]
