from flask import current_app as app


class Tag:
    def __init__(self, pid, cid):
        """Initialize a new Tag instance linking a product ID (pid) with a category ID (cid)."""
        self.pid = pid
        self.cid = cid


    @staticmethod
    def getByProducts(pid):
        """Retrieve all tags associated with a specific product ID."""
        rows = app.db.execute('''
            SELECT pid, cid
            FROM Tags
            WHERE pid = :pid
            ''', pid=pid)
        return [Tag(*row) for row in rows]
    
    
    @staticmethod
    def getByTags(cid):
        """Retrieve a tag by category ID, returning the first associated product-tag pair."""
        rows = app.db.execute('''
            SELECT pid, cid
            FROM Tags
            WHERE cid = :cid
            ''', cid=cid)
        return Tag(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def add_new_tag(pid, cid):
        """Add a new tag linking a product with a category and return the new tag instance."""
        try:
            rows = app.db.execute("""
                INSERT INTO Tags(pid, cid)
                VALUES (:pid, :cid)
                """, pid=pid, cid=int(cid))
            return Tag(*(rows[0])) if rows is not None else None
        except Exception as e:
            print(f"Failed to add new tag: {e}")
            return None
    
    
    @staticmethod
    def delete_product_tag(pid):
        """Delete all tags associated with a specific product ID."""
        try:
            app.db.execute("""
                DELETE FROM Tags
                WHERE pid = :pid
                """, pid=pid)
            return True
        except Exception as e:
            print(f"Failed to delete product tags: {e}")
            return False