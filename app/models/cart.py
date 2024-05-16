from flask import current_app as app


class Cart:
    """Class for cart management with methods for CRUD operations related to cart data."""
    
    def __init__(self, id, uid):
        self.id = id
        self.uid = uid


    @staticmethod
    def getById(id):
        """Retrieve a Cart by its ID."""
        rows = app.db.execute('''
            SELECT id, uid
            FROM Carts
            WHERE id = :id
            ''', id=id)
        return Cart(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def getByUser(uid):
        """Retrieve a Cart by the associated user's ID."""
        rows = app.db.execute('''
            SELECT id, uid
            FROM Carts
            WHERE uid = :uid
            ''', uid=uid)
        return Cart(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def register(uid=None):
        """Register a new cart for a user by their user ID and return the cart instance."""
        try:
            rows = app.db.execute("""
                INSERT INTO Carts(uid)
                VALUES(:uid)
                RETURNING id
                """, uid=uid)
            id = rows[0][0]
            return Cart.getById(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
    
    
    @staticmethod
    def has_cart(uid):
        """Check if a user has a cart."""
        rows = app.db.execute('''
            SELECT id, uid 
            FROM Carts 
            WHERE uid = :uid
            ''', uid=uid)
        return len(rows) > 0
    
    
    @staticmethod
    def add_to_cart(cid, invid, unit_price):
        """Add an inventory item to a cart, adjusting quantity if the item already exists."""
        try:
            # Check if the (cid, invid) pair exists in the table
            existing_row = app.db.execute("""
                SELECT quantity FROM Cart_Products
                WHERE cid = :cid AND invid = :invid
            """, cid=cid, invid=invid)
            current_quantity = app.db.execute("""
                SELECT current_quantity FROM Inventories
                WHERE id = :invid
            """, invid=invid)

            if existing_row:
                # If the pair exists, increment the quantity by 1
                updated_quantity = existing_row[0][0] + 1
                if updated_quantity <= current_quantity[0][0]:
                    app.db.execute("""
                        UPDATE Cart_Products
                        SET quantity = :updated_quantity
                        WHERE cid = :cid AND invid = :invid
                    """, updated_quantity=updated_quantity, cid=cid, invid=invid)
                else:
                    return False
            else:
                if current_quantity[0][0] >= 1:
                    # If the pair doesn't exist, insert a new record with quantity 1
                    app.db.execute("""
                        INSERT INTO Cart_Products (cid, invid, quantity, unit_price, in_cart)
                        VALUES (
                            :cid,
                            :invid,
                            1,
                            :unit_price,
                            True
                        )
                    """, cid=cid, invid=invid, unit_price=unit_price)
                
                else:
                    return False
            return True
        except Exception as e:
            print(str(e))
            return False
    
    
    @staticmethod
    def delete_cart_items(cid):
        """Delete all items from a cart that are marked as in cart."""
        try:
            app.db.execute("""
                DELETE FROM Cart_Products
                WHERE cid = :cid AND in_cart = TRUE
            """, cid=cid)
            return True
        except Exception as e:
            print(str(e))
            return False


    @staticmethod
    def edit_quantity_by_invid(cid, invid, quantity):
        """Edit the quantity of a specific item in the cart."""
        try:
            current_quantity = app.db.execute("""
                SELECT current_quantity FROM Inventories
                WHERE id = :invid
            """, invid=invid)
            if quantity > current_quantity[0][0]:
                return False
            app.db.execute("""
                UPDATE Cart_Products
                SET quantity = :quantity
                WHERE cid = :cid AND invid = :invid
            """, cid=cid, invid=invid, quantity=quantity)

            return True
        except Exception as e:
            print(str(e))
            return False


    @staticmethod
    def remove_product_by_invid(cid, invid):
        """Remove a specific product from the cart by inventory ID."""
        try:
            app.db.execute("""
                DELETE FROM Cart_Products
                WHERE cid = :cid AND invid = :invid
            """, cid=cid, invid=invid)

            return True
        except Exception as e:
            print(str(e))
            return False
        
        
    @staticmethod
    def save_product_for_later(cid, invid):
        """Mark a product in the cart to be saved for later (not for purchase now)."""
        try:
            app.db.execute("""
                UPDATE Cart_Products
                SET in_cart = FALSE
                WHERE cid = :cid AND invid = :invid;
            """, cid=cid, invid=invid)
            return True
        except Exception as e:
            print(str(e))
            return False
        
        
    @staticmethod
    def move_product_to_cart(cid, invid):
        """Move a product back to active cart status from saved for later."""
        try:
            app.db.execute("""
                UPDATE Cart_Products
                SET in_cart = TRUE
                WHERE cid = :cid AND invid = :invid;
            """, cid=cid, invid=invid)
            return True
        except Exception as e:
            print(str(e))
            return False

