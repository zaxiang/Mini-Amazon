from flask import current_app as app
from collections import defaultdict


class Review:
    def __init__(self, id, uid, invid, rating, review, time_created, upvote=0):
        """Initialize a new Review instance with various attributes."""
        self.id = id
        self.uid = uid
        self.invid = invid
        self.rating = rating
        self.review = review
        self.time_created = time_created
        self.upvote = upvote


    @staticmethod
    def getById(id):
        """Retrieve a single review by its ID."""
        rows = app.db.execute('''
            SELECT id, uid, invid, rating, review, time_created, upvote
            FROM Reviews
            WHERE id = :id
            ''', id=id)
        return Review(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def getByInventory(invid):
        """Retrieve all reviews for a specific inventory item, sorted by upvotes and then by creation time."""
        rows = app.db.execute('''
            SELECT id, uid, invid, rating, review, time_created, upvote
            FROM Reviews
            WHERE invid = :invid
            ORDER BY upvote DESC, time_created DESC
            ''', invid=invid)
        if not rows:
            return []

        reviews = [Review(*row) for row in rows]
        
        # default: the top 3 most helpful reviews would be shown first, 
        # and then the most recent following these.
        if len(reviews) > 3:
            top_three = reviews[:3]
            remaining_reviews = sorted(reviews[3:], key=lambda x: x.time_created, reverse=True)
            reviews = top_three + remaining_reviews
        
        return reviews

    
    @staticmethod
    def deleteById(id):
        """Delete a review by its ID and return True if successful."""
        try:
            result = app.db.execute('''
                DELETE FROM Reviews
                WHERE id = :id
                RETURNING id
            ''', id=id)
            return True if result else False
        except Exception as e:
            print(f"An error occurred while deleting review {id}: {e}")
            return False


    @staticmethod
    def getByUser(uid):
        """Retrieve all reviews made by a specific user, ordered by the time they were created."""
        rows = app.db.execute('''
            SELECT id, uid, invid, rating, review, time_created, upvote
            FROM Reviews
            WHERE uid = :uid
            ORDER BY time_created DESC
            ''', uid=uid)
        return [Review(*row) for row in rows]


    @staticmethod
    def get_most_recent_k_review(uid,k):
        """Retrieve the most recent 'k' reviews made by a specific user."""
        rows = app.db.execute('''
            SELECT id, uid, invid, rating, review, time_created, upvote
            FROM Reviews
            WHERE uid = :uid
            ORDER BY time_created DESC
            LIMIT :limit
        ''', uid=uid, limit=k)
        
        if rows:
            return [Review(*row) for row in rows]
        else:
            return None


    @staticmethod
    def update_review(review_id, rating, review_text):
        """Update the rating and text of an existing review and reset its creation timestamp."""
        try:
            result = app.db.execute('''
                UPDATE Reviews
                SET rating = :rating, review = :review, time_created = CURRENT_TIMESTAMP
                WHERE id = :review_id
                RETURNING id
            ''', rating=rating, review=review_text, review_id=review_id)
            return True if result else False
        except Exception as e:
            print(f"An error occurred while updating review {review_id}: {e}")
            return False


    @staticmethod
    def add_review(uid, invid, rating, review_text):
        """Add a new review for an inventory item by a user."""
        try:
            result = app.db.execute('''
                INSERT INTO Reviews(uid, invid, rating, review)
                VALUES(:uid, :invid ,:rating, :review)
                RETURNING id
            ''', uid=uid, invid = invid, rating=rating, review=review_text)
            id = result[0][0]
            return Review.getById(id)
        except Exception as e:
            print(f"An error occurred while adding a review: {e}")
            return None


    @staticmethod
    def review_exists_for_user_and_inventory(uid, invid):
        """Check if a review already exists for a user and an inventory item."""
        row = app.db.execute('''
            SELECT id
            FROM Reviews
            WHERE uid = :uid AND invid = :invid
            ''', uid=uid, invid=invid)
        return bool(row)


    @staticmethod
    def check_user_upvote(user_id, review_id):
        """Check if a user has already upvoted a review."""
        result = app.db.execute('''
            SELECT 1 FROM ReviewUpvotes
            WHERE user_id = :user_id AND review_id = :review_id
        ''', user_id=user_id, review_id=review_id)
        return bool(result)


    @staticmethod
    def add_upvote(review_id, user_id):
        """Add an upvote to a review from a user and update the review's upvote count."""
        try:
            # Add record to ReviewUpvotes
            app.db.execute('''
                INSERT INTO ReviewUpvotes (review_id, user_id)
                VALUES (:review_id, :user_id)
            ''', review_id=review_id, user_id=user_id)
            # Increment upvote count in Reviews
            app.db.execute('''
                UPDATE Reviews
                SET upvote = upvote + 1
                WHERE id = :review_id
            ''', review_id=review_id)
            return True
        except Exception as e:
            # Handle errors like duplicate insertion attempts
            print(f"Error adding upvote: {e}")
            return False


    @staticmethod
    def add_images_to_review(rid, image_ids):
        """Adds image references to a review."""
        try:
            # Insert new images
            for imgid in image_ids:
                app.db.execute('''
                    INSERT INTO Review_Images (rid, imgid)
                    VALUES (:rid, :imgid)
                ''', rid=rid, imgid=imgid)
            return True
        except Exception as e:
            print(f"Error in adding images to review: {e}")
            return False
