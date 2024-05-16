from flask import current_app as app

class Seller:
    """Class representing sellers with methods for database interactions related to seller data."""

    def __init__(self, id, uid):
        """Initialize a Seller instance.
        Args:
            id (int): Seller's ID in the database.
            uid (int): User ID associated with the seller.
        """
        self.id = id
        self.uid = uid


    @staticmethod
    def getById(id):
        """Retrieve a seller by their seller ID.
        Args:
            id (int): The seller's ID to search for.
        Returns:
            Seller: A Seller instance corresponding to the given ID if found, else None.
        """
        rows = app.db.execute('''
            SELECT id, uid
            FROM Sellers
            WHERE id = :id
            ''', id=id)
        return Seller(*(rows[0])) if rows else None
    
    
    @staticmethod
    def getByUid(uid):
        """Retrieve a seller by their user ID.
        Args:
            uid (int): The user ID to search for a seller record.
        Returns:
            Seller: A Seller instance corresponding to the given user ID if found, else None.
        """
        rows = app.db.execute('''
            SELECT id, uid
            FROM Sellers
            WHERE uid = :uid
            ''', uid=uid)
        return Seller(*(rows[0])) if rows else None
    
    
    @staticmethod
    def register(uid):
        """Registers a new seller with a given user ID.
        Args:
            uid (int): User ID of the new seller to register.
        Returns:
            Seller: A new Seller instance if registration is successful, else None.
        """
        try:
            rows = app.db.execute("""
                INSERT INTO Sellers(uid)
                VALUES(:uid)
                RETURNING id
                """, uid=uid)
            id = rows[0][0]
            return Seller.getById(id)
        except Exception as e:
            print(f"Failed to register new seller: {e}")
            return None
    
    
    @staticmethod
    def is_seller(uid):
        """Checks if a given user ID corresponds to a seller.
        Args:
            uid (int): User ID to check against seller records.
        Returns:
            bool: True if the user is a seller, otherwise False.
        """
        rows = app.db.execute('''
            SELECT id, uid 
            FROM Sellers 
            WHERE uid = :uid
            ''', uid=uid)
        return len(rows) > 0
    
    
    @staticmethod
    def get_seller_product_ids(sid):
        """Get product the current seller sells.
        Args:
            sid (int): Seller ID 
        Returns:
            list: List of pid the current seller sells.
        """
        rows = app.db.execute('''
            SELECT pid FROM Inventories WHERE sid = :sid
        ''', sid=sid)
        return [row[0] for row in rows]  