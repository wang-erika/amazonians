from flask import current_app as app

# review class
class Review:

    def __init__(self, uid, pid, rating, review, date):
        self.pid = pid
        self.uid = uid
        self.date = date
        self.rating = rating
        self.review = review

 # Check if the user has purchased the product
    @staticmethod
    def user_purchased_product(uid, pid):
        rows = app.db.execute('''
SELECT *
FROM Purchases
WHERE uid = :uid
AND pid = :pid
''',
                              uid = uid, 
                              pid = pid)
    # if the user has bought the product at least once
        if len(rows) > 0:
            return True

# get all product reviews since a certain time
    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT uid, pid, review_time, review_content
FROM RatesProduct
WHERE uid = :uid
AND review_time >= :since
ORDER BY review_time DESC
''',
                              uid=uid,
                              since=since)
        return [Review(*row) for row in rows]

# get a users recent product reviews
    @staticmethod
    def get_recent_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct 
WHERE uid = :uid
ORDER BY date DESC
LIMIT 5
''',
                              uid = uid)
        return [Review(*row) for row in rows]

#get specific product review from uid and pid
    @staticmethod
    def get_product_review(uid, pid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct 
WHERE uid = :uid
AND pid = :pid
ORDER BY date DESC
''',
                              uid = uid, 
                              pid = pid)
        return Review(*(rows[0])) if rows is not None else None

# get all the product reviews of a user
    @staticmethod
    def get_all_product_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct r, Products p
WHERE r.uid = :uid
AND p.id = r.pid
ORDER BY date DESC
''',
                              uid = uid)
        return rows


#add product review to db
    @staticmethod
    def add_new_product_review(uid, pid, date, rating, review):
            
        # then add this product into RatesProduct
        try:
            rows = app.db.execute("""
INSERT INTO RatesProduct(uid, pid, rating, review, date)
VALUES(:uid, :pid, :rating, :review, :date)
""",
                                uid = uid, 
                                pid = pid, 
                                date = date, 
                                rating = rating, 
                                review = review)
            
            pid = rows[0][1]
            return pid

        except Exception as e:
            print(str(e))
            return None

# given uid and pid, delete review from RatesProduct
    @staticmethod
    def delete_product_review(uid, pid):
        # Delete review
        rows = app.db.execute('''
delete from RatesProduct
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid)

# check if there is already a product review for this user
    @staticmethod
    def has_product_review(uid, pid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct 
WHERE uid = :uid
AND pid = :pid
''',
                              uid = uid, 
                              pid = pid)
    # if there is already a product review from this user
        if len(rows) > 0:
            return True


# get matching product name with pid
    @staticmethod
    def get_product_name(pid):
        rows = app.db.execute('''
SELECT p.name
FROM Products p
WHERE p.id = :pid
''', 
                              pid = pid)
        if len(rows) == 0:
            return "can't find product name"
        return rows[0]


# get summary stats for a product
    @staticmethod
    def get_product_stats(pid):
        rows = app.db.execute('''
SELECT avg(rating) as average
FROM RatesProduct
WHERE pid = :pid
''', 
                              pid = pid)
        if rows[0][0] is not None:
            return round(rows[0][0],2)
        return "no ratings yet"


# get number of ratings for a product
    @staticmethod
    def get_number_ratings(pid):
        rows = app.db.execute('''
SELECT count(rating) as count
FROM RatesProduct
WHERE pid = :pid
''', 
                              pid = pid)
        return rows[0][0]


# get all reviews from all users for a product
    @staticmethod
    def get_summary_reviews(pid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct
WHERE pid = :pid
ORDER BY date DESC
''', 
                              pid = pid)
        return rows




# our seller review class
class Seller_Review:

    def __init__(self, uid, sid, rating, review, date):
        self.sid = sid
        self.uid = uid
        self.date = date
        self.rating= rating
        self.review = review

# get all seller reviews for a user since a certain time
    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT uid, sid, review_time, review_content
FROM RatesProduct
WHERE uid = :uid
AND review_time >= :since
ORDER BY review_time DESC
''',
                              uid=uid,
                              since=since)
        return [Seller_Review(*row) for row in rows]


# get 5 most recent seller reviews of a user
    @staticmethod
    def get_seller_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesSeller
WHERE uid = :uid
ORDER BY date DESC
LIMIT 5
''',
                              uid=uid)
        return [Seller_Review(*row) for row in rows]

# get the seller review given a uid and sid
    @staticmethod
    def get_seller_review(uid, sid):
        rows = app.db.execute('''
SELECT *
FROM RatesSeller
WHERE uid = :uid
AND sid = :sid
''',
                              uid = uid, 
                              sid = sid)
        return Seller_Review(*(rows[0])) if rows is not None else None

# get all seller reviews for a user
    @staticmethod
    def get_all_seller_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesSeller r, Users u
WHERE r.uid = :uid
AND r.sid = u.id
ORDER BY date DESC
''',
                              uid=uid)
        return rows

#add seller review to db
    @staticmethod
    def add_new_seller_review(uid, sid, date, rating, review):
            
        # then add this product into RatesSeller
        try:
            rows = app.db.execute("""
INSERT INTO RatesSeller(uid, sid, rating, review, date)
VALUES(:uid, :sid, :rating, :review, :date)
""",
                                uid = uid, 
                                sid = sid, 
                                date = date, 
                                rating = rating, 
                                review = review)
            
            sid = rows[0][1]
            return sid

        except Exception as e:
            print(str(e))
            return None

# given uid and pid, delete review from RatesSeller
    @staticmethod
    def delete_seller_review(uid, sid):
        # Delete review
        rows = app.db.execute('''
delete from RatesSeller
where uid = :uid and sid = :sid;
''',
                              uid=uid,
                              sid=sid)

# check if there is already a seller review
    @staticmethod
    def has_seller_review(uid, sid):
        rows = app.db.execute('''
SELECT *
FROM RatesSeller
WHERE uid = :uid
AND sid = :sid
''',
                              uid = uid, 
                              sid = sid)
    # if there is already a seller review from this user
        if len(rows) > 0:
            return True


 # Check if the user has purchased from the seller
    @staticmethod
    def user_purchased_seller(uid, sid):
        rows = app.db.execute('''
SELECT *
FROM Purchases, Inventory
WHERE Purchases.uid = :uid
AND Purchases.pid = Inventory.pid
AND Inventory.sid = :sid
''',
                              uid = uid, 
                              sid = sid)
    # if the user has bought from seller at least once
        if len(rows) > 0:
            return True

 # Get the seller from the sid
    @staticmethod
    def get_seller_name(sid):
        rows = app.db.execute('''
SELECT Users.full_name
FROM Sellers, Users
WHERE Sellers.id = :sid
AND Sellers.id = Users.id
''',
                              sid = sid)
        return rows[0][0]





    








