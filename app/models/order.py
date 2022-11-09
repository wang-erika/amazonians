import os
from flask import current_app as app
from werkzeug.utils import secure_filename


class Order:
    def __init__(self, id, uid, date_ordered, fulfilled):
        self.id = id
        self.uid = uid
        self.date_ordered = date_ordered 
        self.fulfilled = fulfilled


    @staticmethod
    def get_orders_by_uid(uid):
        rows = app.db.execute('''
select id, uid, date_ordered, fulfilled
from Orders
where uid = :uid
order by date_ordered desc
''',
                              uid=uid)
        return [Order(*row) for row in rows]
    
