from flask import current_app as app

class Review:

    def __init__(self, pid, uid, dates, rating, review):
        self.pid = pid
        self.uid = uid
        self.dates = dates
        self.rating= rating
        self.review = review

 #*  @staticmethod
 #   def get(uid):
 #       rows = app.db.execute('''
#SELECT uid, pid, review_time, review_content
#FROM RatesProduct
# WHERE id = :id
# ''',
  #                            id=id)
 #       return Review(*(rows[0])) if rows else None

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

    @staticmethod
    def get_recent_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct 
WHERE uid = :uid
ORDER BY dates DESC
LIMIT 5
''',
                              uid = uid)
        return [Review(*row) for row in rows]

    @staticmethod
    def get_all_product_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesProduct 
WHERE uid = :uid
ORDER BY dates DESC
''',
                              uid = uid)
        return [Review(*row) for row in rows]


#add product review to db
    @staticmethod
    def add_new_product_review(uid, pid, dates, rating, review):
            
        # then add this product into RatesProduct
        try:
            rows = app.db.execute("""
INSERT INTO RatesProduct(pid, uid, dates, rating, review)
VALUES(:pid, :uid, :dates, :rating, :review)
""",
                                pid = pid, 
                                uid = uid, 
                                dates = dates, 
                                rating = rating, 
                                review = review)
            
            pid = rows[0][0]
            return pid

        except Exception as e:
            print(str(e))
            return None

# given uid and pid, delete reiew from RatesProduct
    @staticmethod
    def delete_product_review(uid, pid):
        # Delete review
        rows = app.db.execute('''
delete from RatesProduct
where uid = :uid and pid = :pid;
''',
                              uid=uid,
                              pid=pid)


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


class Seller_Review:

    def __init__(self, sid, uid, dates, rating, review):
        self.sid = sid
        self.uid = uid
        self.dates = dates
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
ORDER BY dates DESC
LIMIT 5
''',
                              uid=uid)
        return [Seller_Review(*row) for row in rows]

    @staticmethod
    def get_all_seller_reviews(uid):
        rows = app.db.execute('''
SELECT *
FROM RatesSeller
WHERE uid = :uid
ORDER BY dates DESC
''',
                              uid=uid)
        return [Seller_Review(*row) for row in rows]




