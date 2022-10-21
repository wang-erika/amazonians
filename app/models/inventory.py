from flask import current_app as app


class Inventory:
    def __init__(self, sid, pid, quantity):
        self.sid = sid
        self.pid = pid
        self.quantity = quantity

    # get a single inventory tuple
    @staticmethod
    def get(sid, pid):
        rows = app.db.execute('''
SELECT sid, pid, quantity
FROM Inventory
WHERE pid = :pid AND sid = :sid
''',
                              pid=pid,
                              sid=sid)
        return Inventory(*(rows[0])) if rows else None

    # get tuples associated with a product id
    # TODO should prob join with Products to get product info once Havish finishes that
    @staticmethod
    def get_by_pid(pid):
        rows = app.db.execute('''
SELECT sid, pid, quantity
FROM Inventory
WHERE pid = :pid
''',
                              pid=pid)
        return [Inventory(*row) for row in rows]

    # given id of seller, return list of products in their inventory (and quantity)
    @staticmethod
    def get_by_sid(sid):
        rows = app.db.execute('''
SELECT sid, pid, quantity
FROM Inventory
WHERE sid = :sid
''',
                              sid=sid)
        return [Inventory(*row) for row in rows]
