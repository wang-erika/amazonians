from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, full_name, email, balance, address):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.balance = balance
        self.address = address

    #given email, password, return user data
    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, full_name, email, balance, address
FROM Users
WHERE email = :email
""",
                              email=email)

        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    #given email, check if email is in db
    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    #given fn, ln, email, pw, try to register if email is not used already
    @staticmethod
    def register(firstname, lastname, email, password):
        try:
            rows = app.db.execute("""
INSERT INTO Users(full_name, email, password)
VALUES(:full_name, :email, :password)
RETURNING id
""",
                                  full_name = firstname + " " + lastname,
                                  email=email,
                                  password=generate_password_hash(password))
            
            id = rows[0][0]
            return User.get(id)

        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    #update user information
    @staticmethod
    def update(id, full_name, email, address, password):
        rows = app.db.execute('''
update Users
set email = :email, full_name = :full_name, address = :address, password = :password
where id = :id;
''',
                                  id=id,
                                  email=email)
        return id

    #given id, balance, and amount, edit the user's balance
    @staticmethod
    def edit_balance(id, amount, balance):
        rows = app.db.execute('''
update Users
set balance = :amount
where id = :id;
''',
                                  id=id,
                                  amount=balance + amount)
        return rows

    #given id and amount, edit the users alance DONOTCHANGE
    @staticmethod
    def update_balance(id, amount):
        rows = app.db.execute('''
update Users
set balance = :amount
where id = :id;
''',
                                  id=id,
                                  amount=amount)
        return rows
    
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, full_name, email, balance, address
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    #get all of user's attributes
    @staticmethod
    def get_all(id):
        rows = app.db.execute("""
SELECT id, full_name, email, balance, address
FROM Users
WHERE id = :id
""",
                              id=id)
        return [User(*row) for row in rows]