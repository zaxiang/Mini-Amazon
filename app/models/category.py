from flask import current_app as app


class Category:
    def __init__(self, id, label):
        """Initialize a new Category instance with a unique ID and a label."""
        self.id = id
        self.label = label


    @staticmethod
    def get(id):
        """Retrieve a Category by its ID."""
        rows = app.db.execute('''
            SELECT id, label
            FROM Categories
            WHERE id = :id
            ''', id=id)
        return Category(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def get_all():
        """Retrieve all Categories, ordered by their labels."""
        rows = app.db.execute('''
            SELECT id, label
            FROM Categories
            ORDER BY label
            ''')
        return [Category(*row) for row in rows]
    
    
    @staticmethod
    def getExistCategories():
        """Retrieve distinct categories that are used in existing inventories, ordered by label."""
        rows = app.db.execute('''
            SELECT DISTINCT c.id, c.label
            FROM Inventories i
            JOIN Products p ON i.pid = p.id
            JOIN Tags t ON p.id = t.pid
            JOIN Categories c ON t.cid = c.id
            ORDER BY label
            ''')
        return [Category(*row) for row in rows]
    
    
    @staticmethod
    def get_user_ordered_product_category(user_id):
        """Retrieve distinct categories of products ordered by a specific user, including an 'All Categories' option."""
        rows = app.db.execute('''
            SELECT DISTINCT c.id, c.label
            FROM Categories c
            JOIN Tags t ON t.cid = c.id
            JOIN Products p ON p.id = t.pid
            JOIN Inventories i ON i.pid = p.id
            JOIN Order_Products op ON op.invid = i.id
            JOIN Orders o ON o.id = op.oid
            WHERE o.uid = :user_id
            ORDER BY label
            ''', user_id=user_id)
        all_categories = Category(-1, "All Categories")
        return [all_categories] + [Category(*row) for row in rows]
