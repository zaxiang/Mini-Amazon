from flask import current_app as app
from werkzeug.utils import secure_filename
import os


class Image:
    def __init__(self, id, content):
        """Initialize a new Image instance with an ID and file path/content."""
        self.id = id
        self.content = content
    
    
    @staticmethod
    def save_image(file, imgid):
        """Save an image to the designated upload folder."""
        if file:
            filename = secure_filename(f'{imgid}.jpeg')
            upload_folder = 'app/static/images'
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            return filename
        return None
    
        
    @staticmethod
    def get_all():
        """Retrieve all image records from the database."""
        rows = app.db.execute('''
            SELECT id, content
            FROM Images
        ''')
        return [Image(*row) for row in rows] if rows else None


    @staticmethod
    def get(id):
        """Retrieve a single image by its ID."""
        rows = app.db.execute('''
            SELECT id, content
            FROM Images
            WHERE id = :id
            ''', id=id)
        return Image(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def add_image(file):
        """Add a new image to the database, saving it under a filename based on its database ID."""
        try:
            # Insert a placeholder record to generate an ID
            result = app.db.execute('''
                INSERT INTO Images (content)
                VALUES ('placeholder')
                RETURNING id
            ''')
            imgid = result[0][0]

            # Save the file with the new ID
            filename = Image.save_image(file, imgid)
            if not filename:
                raise Exception("Failed to save image.")

            # Update the record with the correct filename
            app.db.execute('''
                UPDATE Images
                SET content = :content
                WHERE id = :id
            ''', content=filename, id=imgid)

            return Image(imgid, filename)
        except Exception as e:
            print(f"Error adding image: {e}")
            return None
        
        
    @staticmethod
    def delete_image(id):
        """Delete an image record from the database by its ID."""
        try:
            app.db.execute('''
                DELETE FROM Images
                WHERE id = :id
            ''', id=id)
        except Exception as e:
            print(f"Error deleting image: {e}")

    
    ## Product
    @staticmethod
    def get_product_image(pid, display=True):
        """Retrieve the main image for a product; if display is True, return a single Image instance."""
        rows = app.db.execute('''
            SELECT i.id, i.content
            FROM images i
            JOIN products p ON i.id = p.imgid
            WHERE p.id = :pid
            ''',
        pid=pid)
        if display:
            return Image(*(rows[0])) if rows is not None else None
        else:
            return [Image(*row) for row in rows]
    
    
    ## Inventory
    @staticmethod
    def get_inventory_image(invid, display=True):
        """Retrieve the main image for an inventory item; if display is True, return a single Image instance."""
        rows = app.db.execute('''
            SELECT i.id, i.content
            FROM images i
            JOIN inventory_images ii ON i.id = ii.imgid
            WHERE ii.invid = :invid
            ''',
        invid=invid)
        if display:
            return Image(*(rows[0])) if rows is not None else None
        else:
            return [Image(*row) for row in rows]
    
    
    @staticmethod
    def has_inventory_images(invid):
        """Check if there are any images linked to a specific inventory item."""
        rows = app.db.execute('''
            SELECT i.id, i.content
            FROM images i
            JOIN inventory_images ii ON i.id = ii.imgid
            WHERE ii.invid = :invid
            ''', invid=invid)
        return len(rows) > 0
    
    
    ## Feedback
    @staticmethod
    def get_feedback_image(fid):
        """Retrieve all images linked to a feedback entry."""
        rows = app.db.execute('''
            SELECT i.id, i.content
            FROM images i
            JOIN feedback_images fi ON i.id = fi.imgid
            WHERE fi.fid = :fid
            ''',fid=fid)
        return [Image(*row) for row in rows]


    ## Review
    @staticmethod
    def get_review_image(rid):
        """Retrieve all images linked to a review entry."""
        rows = app.db.execute('''
            SELECT i.id, i.content
            FROM images i
            JOIN review_images ri ON i.id = ri.imgid
            WHERE ri.rid = :rid
            ''',rid=rid)
        return [Image(*row) for row in rows]