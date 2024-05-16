from flask import current_app as app
from collections import defaultdict


class Feedback:
    def __init__(self, id, uid, sid, rating, review ,time_created, upvote=0):
        """Initialize a new Feedback instance with various attributes."""
        self.id = id
        self.uid = uid
        self.sid = sid
        self.rating = rating
        self.review = review
        self.time_created = time_created
        self.upvote = upvote


    # Get inventory information
    @staticmethod
    def getById(id):
        """Retrieve a single feedback entry by its ID."""
        rows = app.db.execute('''
            SELECT id, uid, sid, rating, review, time_created, upvote
            FROM Feedbacks
            WHERE id = :id
            ''', id=id)
        return Feedback(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def getBySeller(sid):
        """Retrieve all feedback entries for a specific seller, sorted by upvotes and then by creation time."""
        rows = app.db.execute('''
            SELECT id, uid, sid, rating, review, time_created, upvote
            FROM Feedbacks
            WHERE sid = :sid
            ORDER BY upvote DESC, time_created DESC
            ''', sid=sid)
        feedbacks = [Feedback(*row) for row in rows]
        
        # default: the top 3 most helpful reviews would be shown first, 
        # and then the most recent following these.
        if len(feedbacks) > 3:
            top_three = feedbacks[:3]
            remaining_feedbacks = sorted(feedbacks[3:], key=lambda x: x.time_created, reverse=True)
            feedbacks = top_three + remaining_feedbacks
        
        return feedbacks
    
    
    @staticmethod
    def getByUser(uid):
        """Retrieve all feedback entries made by a specific user, ordered by the time they were created."""
        rows = app.db.execute('''
            SELECT id, uid, sid, rating, review, time_created, upvote
            FROM Feedbacks
            WHERE uid = :uid
            ORDER BY time_created DESC
            ''', uid=uid)
        return [Feedback(*row) for row in rows]


    @staticmethod
    def get_most_recent_k_feedback(uid,k):
        """Retrieve the most recent 'k' feedback entries made by a specific user."""
        rows = app.db.execute('''
            SELECT id, uid, sid, rating, review, time_created, upvote
            FROM Feedbacks
            WHERE uid = :uid
            ORDER BY time_created DESC
            LIMIT :limit
        ''', uid=uid, limit=k)
        
        if rows:
            return [Feedback(*row) for row in rows]
        else:
            return None
    
    
    @staticmethod
    def add_feedback(uid, sid, rating, review_text):
        """Add a new feedback entry for a seller by a user and return the new Feedback instance."""
        try:
            result = app.db.execute('''
                INSERT INTO Feedbacks(uid, sid, rating, review, time_created)
                VALUES(:uid, :sid, :rating, :review, CURRENT_TIMESTAMP)
                RETURNING id
            ''', uid=uid, sid=sid, rating=rating, review=review_text)
            id = result[0][0]
            return Feedback.getById(id)
        except Exception as e:
            print(f"An error occurred while adding feedback: {e}")
            return None


    @staticmethod
    def feedback_exists_for_user_and_seller(uid, sid):
        """Check if a feedback already exists for a user and a seller."""
        row = app.db.execute('''
            SELECT id
            FROM Feedbacks
            WHERE uid = :uid AND sid = :sid
            ''', uid=uid, sid=sid)
        return bool(row)
    
    
    @staticmethod
    def update_feedback(feedback_id, rating, review_text):
        """Update the rating and text of an existing feedback entry."""
        try:
            result = app.db.execute('''
                UPDATE Feedbacks
                SET rating = :rating, review = :review, time_created = CURRENT_TIMESTAMP
                WHERE id = :feedback_id
                RETURNING id
            ''', rating=rating, review=review_text, feedback_id=feedback_id)
            return True if result else False
        except Exception as e:
            print(f"An error occurred while updating feedback {feedback_id}: {e}")
            return False
         
            
    @staticmethod
    def deleteById(id):
        """Delete a feedback entry by its ID."""
        try:
            result = app.db.execute('''
                DELETE FROM Feedbacks
                WHERE id = :id
                RETURNING id
            ''', id=id)
            return True if result else False
        except Exception as e:
            print(f"An error occurred while deleting feedback {id}: {e}")
            return False


    @staticmethod
    def check_user_upvote(user_id, feedback_id):
        """Check if a user has already upvoted a specific feedback entry."""
        result = app.db.execute('''
            SELECT 1 FROM FeedbackUpvotes
            WHERE user_id = :user_id AND feedback_id = :feedback_id
        ''', user_id=user_id, feedback_id=feedback_id)
        return bool(result)


    @staticmethod
    def add_upvote(feedback_id, user_id):
        """Add an upvote to a feedback entry and update the feedback's upvote count."""
        try:
            # Add record to FeedbackUpvotes
            app.db.execute('''
                INSERT INTO FeedbackUpvotes (feedback_id, user_id)
                VALUES (:feedback_id, :user_id)
            ''', feedback_id=feedback_id, user_id=user_id)
            # Increment upvote count in Feedback
            app.db.execute('''
                UPDATE Feedbacks
                SET upvote = upvote + 1
                WHERE id = :feedback_id
            ''', feedback_id=feedback_id)
            return True
        except Exception as e:
            # Handle errors like duplicate insertion attempts
            print(f"Error adding upvote: {e}")
            return False
    
    
    @staticmethod
    def add_images_to_feedback(fid, image_ids):
        """Adds image references to a feedback."""
        try:
            # Insert new images
            for imgid in image_ids:
                app.db.execute('''
                    INSERT INTO Feedback_Images (fid, imgid)
                    VALUES (:fid, :imgid)
                ''', fid=fid, imgid=imgid)
            return True
        except Exception as e:
            print(f"Error in adding images to feedback: {e}")
            return False