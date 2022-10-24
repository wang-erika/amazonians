from flask import current_app as app


class Review:
    """
    This is just a TEMPLATE for Review, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, uid, pid, review_time, rating, review_content):
        self.uid = uid
        self.pid = pid
        self.review_time = review_time
        self.rating= rating
        self.review_content = review_content

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
SELECT uid, pid, dates, rating, review
FROM RatesProduct
WHERE uid = :uid
ORDER BY dates DESC
LIMIT 5
''',
                              uid=uid)
        return [Review(*row) for row in rows]
