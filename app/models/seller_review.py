from flask import current_app as app
class Seller_Review:

    def __init__(self, uid, sid, rating, review, date):
        self.sid = sid
        self.uid = uid
        self.date = date
        self.rating= rating
        self.review = review

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
        return Review(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all_seller_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesSeller
WHERE uid = :uid
ORDER BY date DESC
''',
                              uid=uid)
        return [Seller_Review(*row) for row in rows]

#add product review to db
    @staticmethod
    def add_new_seller_review(uid, sid, date, rating, review):
            
        # then add this product into RatesProduct
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

# given uid and pid, delete review from Rates
    @staticmethod
    def delete_seller_review(uid, sid):
        # Delete review
        rows = app.db.execute('''
delete from RatesSeller
where uid = :uid and sid = :sid;
''',
                              uid=uid,
                              sid=sid)

# check if there is already a product review
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
    # if there is already a product review from this user
        if len(rows) > 0:
            return True





