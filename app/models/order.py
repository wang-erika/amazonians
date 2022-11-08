import os
from flask import current_app as app
from werkzeug.utils import secure_filename


class Order:
    def __init__(self, id, sid, uid, pid, quantity, date_ordered, 
                fulfilled, unit_price_at_time_of_payment, u_address, u_full_name,
                p_image, p_category, p_name, p_description):
        self.id = id
        self.sid = sid
        self.uid = uid
        self.pid = pid
        self.quantity = quantity
        self.date_ordered = date_ordered
        self.fulfilled = fulfilled
        self.unit_price_at_time_of_payment = unit_price_at_time_of_payment
        self.u_address = u_address
        self.u_full_name = u_full_name
        self.p_image = p_image
        self.p_category = p_category
        self.p_name = p_name
        self.p_description = p_description
    
    
    # given id of seller, return list of orders involving this 
    # seller IN REVERSE CHRONOLOGICAL ORDER
    @staticmethod
    def get_orders_by_sid(sid):
        rows = app.db.execute('''
select Orders.id, Orders.sid, Orders.uid, Orders.pid, Orders.quantity, Orders.date_ordered,
    Orders.fulfilled, Orders.unit_price_at_time_of_payment, Users.address, Users.full_name,
    Products.image, Products.category, Products.name, Products.description
from Orders join Products
    on Orders.pid = Products.id 
    join Users
    on Orders.uid = Users.id
where sid = :sid
order by Orders.date_ordered desc;
''',
                              sid=sid)
        return [Order(*row) for row in rows]

    # given order id, toggle fulfilled status
    @staticmethod
    def toggle_order_fulfilled(id):
        # Get current status
        status = app.db.execute('''
select fulfilled
from Orders
where id = :id
''',
                              id=id)

        # toggle
        status = 'f' if (status[0][0]) else 't'

        rows = app.db.execute('''
update Orders
set fulfilled = :fulfilled
where id = :id;
''',
                              id=id,
                              fulfilled=status)
