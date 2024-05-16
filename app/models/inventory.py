from flask import current_app as app
from collections import defaultdict

class Inventory:
    """ Represents an inventory item in the system. """
    def __init__(self, id, sid, pid, current_quantity, price):
        """ Initialize an inventory instance with item details. """
        self.id = id
        self.sid = sid
        self.pid = pid
        self.current_quantity = current_quantity
        self.price = price


    # Methods for retrieving inventory information
    @staticmethod
    def getById(id):
        """ Retrieve an inventory by its ID. """
        rows = app.db.execute('''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            WHERE id = :id
            ''', id=id)
        return Inventory(*(rows[0])) if rows else None
    
    
    @staticmethod
    def getSameProductById(id):
        """ Retrieve inventories of the same product by its id """
        rows = app.db.execute('''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            WHERE pid = (
                SELECT pid
                FROM Inventories
                WHERE id = :id
            );
        ''', id=id)
        return [Inventory(*row) for row in rows]


    @staticmethod
    def getBySeller(sid):
        """ Retrieve inventories by seller ID. """
        rows = app.db.execute('''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            WHERE sid = :sid
            ORDER BY id
            ''', sid=sid)
        return [Inventory(*row) for row in rows]


    @staticmethod
    def getByProduct(pid):
        """ Retrieve inventories by product ID. """
        rows = app.db.execute('''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            WHERE pid = :pid
            ORDER BY id
            ''', pid=pid)
        return [Inventory(*row) for row in rows]
    
    
    @staticmethod
    def traceCreatorInventory(sid, pid):
        """ Get the original seller's product's inventory information. """
        rows = app.db.execute('''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            WHERE pid = :pid
            AND sid = :sid
            ORDER BY id
            ''', sid=sid, pid=pid)
        return Inventory(*(rows[0])) if rows else None


    @staticmethod
    def get_all():
        """ Retrieve all inventories. """
        rows = app.db.execute('''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            ORDER BY id
            ''')
        return [Inventory(*row) for row in rows]


    # Methods for adding or deleting inventory
    @staticmethod
    def addNewInventory(sid, pid, current_quantity, price):
        """ Add a new inventory item. """
        try:
            rows = app.db.execute("""
                INSERT INTO Inventories(sid, pid, current_quantity, price)
                VALUES(:sid, :pid, :current_quantity, :price)
                RETURNING id
                """, sid=sid, pid=pid, current_quantity=current_quantity, price=price)
            id = rows[0][0]
            return Inventory.getById(id)
        except Exception as e:
            print(str(e))
            return None


    @staticmethod
    def deleteById(id):
        """ Delete an inventory by ID. """
        try:
            app.db.execute("""
                DELETE FROM Inventories
                WHERE id = :id
                """, id=id)
            return True
        except Exception as e:
            print(str(e))
            return False


    # Methods for updating inventory details
    @staticmethod
    def update_inventory(invid, new_info):
        """ Update inventory details. """
        try:
            result = app.db.execute("""
                UPDATE Inventories
                SET current_quantity = :current_quantity, price = :price
                WHERE id = :id
                RETURNING id
                """, current_quantity=new_info['current_quantity'],
                price=new_info['price'], id=invid)
            return True
        except Exception as e:
            print(f"Error updating inventory: {e}")
            return False


    @staticmethod
    def update_design(invid, new_info):
        """ Update design details of an inventory. """
        try:
            result = app.db.execute("""
                UPDATE Inventory_Designs
                SET name=:name, description=:description
                WHERE invid = :invid
                RETURNING invid
                """, name=new_info['name'], description=new_info['description'], invid=invid)
            return True
        except Exception as e:
            print(f"Error updating inventory design: {e}")
            return False


    @staticmethod
    def updateQuantity(id, new_quantity):
        """ Update the quantity of an inventory item. """
        try:
            if new_quantity < 0:
                print("Cannot update inventory to a negative quantity.")
                return None
            app.db.execute("""
                UPDATE Inventories
                SET current_quantity = :new_quantity
                WHERE id = :id
                """, id=id, new_quantity=new_quantity)
            return True
        except Exception as e:
            print(str(e))
            return None


    @staticmethod
    def get_order_products(oid):
        """ Fetches products from a specific order.
        Args:
            oid (int): Order ID
        Returns:
            list: List of dictionaries containing product details in the order
        """
        # [Add description about the SQL query and its result structure]
        column_names = ['sid', 'invid', 'name', 'description', 'quantity', 'price', 'status', 'fulfilled_time']
        rows = app.db.execute('''
            SELECT 
                s.id AS sid, 
                i.id AS invid,
                COALESCE(id.name, p.name) AS name, 
                COALESCE(id.description, p.description) AS description, 
                op.quantity AS quantity, 
                op.price AS price,
                op.fulfillment_status AS status,
                CASE 
                    WHEN op.fulfillment_status = 'fulfilled' THEN op.time_fulfilled
                    ELSE NULL
                END AS fulfilled_time
            FROM Order_Products op
            INNER JOIN Inventories i ON op.invid = i.id
            LEFT JOIN Inventory_Designs id ON i.id = id.invid
            INNER JOIN Products p ON i.pid = p.id
            INNER JOIN Sellers s ON i.sid = s.id
            WHERE op.oid = :oid
            ORDER BY price DESC
            ''', oid=oid)
        return [dict(zip(column_names, row)) for row in rows] if rows else None


    @staticmethod
    def get_all_order_products(sid):
        """ Fetches all products from all order for a specific seller.
        Returns:
            list: List of dictionaries containing product details in all order
        """
        # [Add description about the SQL query and its result structure]
        column_names = ['name', 'price', 'quantity']
        rows = app.db.execute('''
            SELECT 
                p.name AS name, 
                op.price AS price,
                SUM(op.quantity) AS quantity
            FROM Order_Products op
            INNER JOIN Inventories i ON op.invid = i.id
            LEFT JOIN Inventory_Designs id ON i.id = id.invid
            INNER JOIN Products p ON i.pid = p.id
            INNER JOIN Sellers s ON i.sid = s.id
            WHERE s.id = :sid
            GROUP BY p.name, op.price
            ORDER BY price DESC
            ''', sid=sid)
        return [dict(zip(column_names, row)) for row in rows] if rows else None


    # Retrieve products from the cart by cart ID
    @staticmethod
    def get_cart_products(cid, in_cart=True):
        """ Fetches products from a specific cart.
        Args:
            cid (int): Cart ID
        Returns:
            list: List of dictionaries containing product details in the cart
        """
        column_names = ['sid', 'name', 'description', 'quantity', 'price', 'invid']
        rows = app.db.execute('''
                SELECT 
                    s.id AS sid, 
                    COALESCE(id.name, p.name) AS name, 
                    COALESCE(id.description, p.description) AS description, 
                    cp.quantity AS quantity, 
                    cp.unit_price AS price,
                    cp.invid
                FROM 
                    Cart_Products cp
                INNER JOIN 
                    Inventories i ON cp.invid = i.id
                LEFT JOIN 
                    Inventory_Designs id ON i.id = id.invid
                INNER JOIN 
                    Products p ON i.pid = p.id
                INNER JOIN 
                    Sellers s ON i.sid = s.id
                WHERE 
                    cp.cid = :cid AND cp.in_cart = :in_cart
                ORDER BY price DESC
                ''', cid=cid, in_cart=in_cart)
        return [dict(zip(column_names, row)) for row in rows] if rows else None


    # Retrieve designs associated with a specific inventory item
    @staticmethod
    def get_inventory_designs(invid):
        """ Fetches design details for a specific inventory item.
        Args:
            invid (int): Inventory ID
        Returns:
            list: List of dictionaries containing design details for the inventory
        """
        column_names = ['invid', 'name', 'description']
        rows = app.db.execute('''
            SELECT 
                i.id AS invid,
                COALESCE(id.name, p.name) AS name, 
                COALESCE(id.description, p.description) AS description
            FROM 
                Inventories i
            LEFT JOIN 
                Inventory_Designs id ON i.id = id.invid
            INNER JOIN 
                Products p ON i.pid = p.id
            WHERE 
                i.id = :invid
            ''', invid=invid)  
        
        return [dict(zip(column_names, row)) for row in rows] if rows else None


    # Retrieve the top K highest priced products across all inventories
    @staticmethod
    def get_top_k_highest_priced_products(k):
        """ Retrieves the highest priced products up to a limit of 'k'.
        Args:
            k (int): Number of top priced products to retrieve
        Returns:
            dict: A dictionary mapping product names to their highest prices
        """
        rows = app.db.execute('''
            SELECT pid, MAX(price) AS max_price
            FROM Inventories
            GROUP BY pid
            ORDER BY max_price DESC
            LIMIT :limit
        ''', limit=k)

        # Map product IDs to their names
        pid_to_name = {}
        for row in rows:
            pid = row[0]
            product_name = app.db.execute('''
                SELECT name
                FROM Products
                WHERE id = :pid
            ''', pid=pid)
            pid_to_name[pid] = product_name

        # Aggregate results
        top_products = defaultdict(list)
        for row in rows:
            pid = row[0]
            max_price = row[1]
            product_name = pid_to_name[pid][0]
            top_products[product_name] = max_price

        return top_products


    # Search inventories by keyword
    @staticmethod
    def getByKeyword(keyword):
        """ Searches inventory items by keyword.
        Args:
            keyword (str): Keyword to search for in product descriptions, names, or categories
        Returns:
            list[Inventory]: A list of Inventory objects that match the keyword
        """
        safe_keyword = f'%{keyword}%'
        rows = app.db.execute('''
            SELECT DISTINCT i.id, i.sid, i.pid, i.current_quantity, i.price
            FROM Inventories i
            JOIN Products p ON i.pid = p.id
            JOIN Tags t ON p.id = t.pid
            JOIN Categories c ON c.id = t.cid
            WHERE p.description LIKE :keyword or c.label LIKE :keyword or p.name LIKE :keyword
            ''', keyword=safe_keyword)
        return [Inventory(*row) for row in rows]


    # Retrieve inventories by category
    @staticmethod
    def getByCategory(cid):
        """ Fetches inventory items associated with a specific category.
        Args:
            cid (int): Category ID
        Returns:
            list[Inventory]: A list of Inventory objects within the specified category
        """
        rows = app.db.execute('''
            SELECT i.id, i.sid, i.pid, i.current_quantity, i.price
            FROM Inventories i
            JOIN Products p ON i.pid = p.id
            JOIN Tags t ON p.id = t.pid
            WHERE t.cid = :cid
            ''', cid=cid)
        return [Inventory(*row) for row in rows]


    # Retrieve inventories sorted by price in ascending or descending order
    @staticmethod
    def getByPrice(order='asc'):
        """ Fetches inventory items sorted by price either in ascending or descending order.
        Args:
            order (str): Sort order, 'asc' for ascending, 'desc' for descending.
        Returns:
            list[Inventory]: A list of Inventory objects sorted by price.
        """
        order_clause = 'ASC' if order == 'asc' else 'DESC'
        query = f'''
            SELECT id, sid, pid, current_quantity, price
            FROM Inventories
            ORDER BY price {order_clause}
        '''
        rows = app.db.execute(query)
        return [Inventory(*row) for row in rows]
    
    
    # Retrieve inventories sorted by average rating in ascending or descending order
    @staticmethod
    def getByRating(order='desc'):
        """ Fetches inventory items sorted by average rating either in ascending or descending order.
        Args:
            order (str): Sort order, 'asc' for ascending, 'desc' for descending.
        Returns:
            list[Inventory]: A list of Inventory objects sorted by average rating.
        """
        order_clause = 'DESC' if order == 'desc' else 'ASC'
        query = f'''
            SELECT 
                i.id AS id,
                i.pid AS pid,
                i.sid AS sid,
                i.current_quantity AS current_quantity,
                i.price AS price
            FROM 
                Inventories i
            LEFT JOIN 
                Reviews r ON i.id = r.invid
            GROUP BY 
                i.id, i.pid, i.sid, i.current_quantity, i.price
            ORDER BY 
                COALESCE(AVG(r.rating), 0) {order_clause};
        '''
        rows = app.db.execute(query)
        return [Inventory(*row) for row in rows]
    
    
    # Retrieve inventories sorted by total sales in ascending or descending order
    @staticmethod
    def getBySales(order='desc'):
        """ Fetches inventory items sorted by total sales either in ascending or descending order.
        Args:
            order (str): Sort order, 'asc' for ascending, 'desc' for descending.
        Returns:
            list[Inventory]: A list of Inventory objects sorted by total sales.
        """
        order_clause = 'DESC' if order == 'desc' else 'ASC'
        query = f'''
            SELECT 
                i.id AS id,
                i.pid AS pid,
                i.sid AS sid,
                i.current_quantity AS current_quantity,
                i.price AS price
            FROM 
                Inventories i
            LEFT JOIN 
                Order_Products op ON i.id = op.invid
            GROUP BY 
                i.id, i.pid, i.sid, i.current_quantity, i.price
            ORDER BY 
                COALESCE(SUM(op.quantity), 0) {order_clause};
        '''
        rows = app.db.execute(query)
        return [Inventory(*row) for row in rows]
    
    
    @staticmethod
    def search_inventory_by_form(sid=None, keyword=None, category=None, sort=None, rating_filter=None, price_min=None, price_max=None):
        """
        Search and filter inventory items based on various criteria including seller ID, keywords in the product name or description,
        category, and sorting by price, rating, or sales volume. Optionally, filter by minimum rating and price range.
        """
        query = """
            SELECT i.id AS id,
                i.pid AS pid,
                i.sid AS sid,
                i.current_quantity AS current_quantity,
                i.price AS price
            FROM Inventories i
            JOIN Products p ON i.pid = p.id
            LEFT JOIN (
                SELECT invid, COALESCE(AVG(rating), 0) AS average_rating,COALESCE(COUNT(id), 0) AS total_reviews
                FROM Reviews
                GROUP BY invid
            ) r ON r.invid = i.id
            LEFT JOIN (
                SELECT invid, COALESCE(SUM(quantity), 0) AS total_sales
                FROM Order_Products
                GROUP BY invid
            ) op ON op.invid = i.id
            WHERE 1=1
        """
        params = {}

        if sid:
            query += " AND i.sid = :sid"
            params['sid'] = sid

        if keyword:
            query += " AND (LOWER(p.name) LIKE :keyword OR LOWER(p.description) LIKE :keyword)"
            params['keyword'] = f'%{keyword.lower()}%'

        if category:
            query += " AND EXISTS (SELECT 1 FROM Tags t JOIN Categories c ON t.cid = c.id WHERE t.pid = p.id AND LOWER(c.label) LIKE :category)"
            params['category'] = f'%{category.lower()}%'

        if rating_filter:
            query += " AND COALESCE(r.average_rating, 0) >= :rating_filter"
            params['rating_filter'] = rating_filter

        if price_min is not None:
            query += " AND i.price >= :price_min"
            params['price_min'] = price_min

        if price_max is not None:
            query += " AND i.price <= :price_max"
            params['price_max'] = price_max

        query += " GROUP BY i.id, i.pid, i.sid, i.current_quantity, i.price, average_rating, total_sales"

        # Handling sorting
        if sort:
            sorting_criteria = []
            if 'price_asc' in sort:
                sorting_criteria.append("i.price ASC")
            if 'price_desc' in sort:
                sorting_criteria.append("i.price DESC")
            if 'rating_asc' in sort:
                sorting_criteria.append("average_rating ASC")
            if 'rating_desc' in sort:
                sorting_criteria.append("average_rating DESC")
            if 'sales_asc' in sort:
                sorting_criteria.append("total_sales ASC")
            if 'sales_desc' in sort:
                sorting_criteria.append("total_sales DESC")

            if sorting_criteria:
                query += " ORDER BY " + ", ".join(sorting_criteria)

        print("Executing SQL:", query)
        print("With parameters:", params)
        rows = app.db.execute(query, **params)

        return [Inventory(*row) for row in rows]
    
    
    # Inventory Designs & Images
    @staticmethod
    def check_exist_design(invid):
        """Check if a design exists for the specified inventory ID."""
        try:
            rows = app.db.execute('''
                SELECT 1 FROM Inventory_Designs WHERE invid = :invid
            ''', invid=invid)
            
            return bool(rows)
        except Exception as e:
            print(f"Error checking existing design: {e}")
            return False
        
        
    @staticmethod
    def add_or_update_design(existing_design, invid, name, description):
        """Adds or updates a design for a specific inventory."""
        try:
            if existing_design:
                # Update existing design
                app.db.execute('''
                    UPDATE Inventory_Designs
                    SET name = :name, description = :description
                    WHERE invid = :invid
                ''', invid=invid, name=name, description=description)
                return True
            else:
                # Insert new design
                app.db.execute('''
                    INSERT INTO Inventory_Designs (invid, name, description)
                    VALUES (:invid, :name, :description)
                ''', invid=invid, name=name, description=description)
                return True
        except Exception as e:
            print(f"Error in adding or updating inventory design: {e}")
            return False
        
        
    @staticmethod
    def add_images_to_inventory(invid, image_ids):
        """Adds image references to an inventory."""
        try:
            # Insert new images
            for imgid in image_ids:
                app.db.execute('''
                    INSERT INTO Inventory_Images (invid, imgid)
                    VALUES (:invid, :imgid)
                ''', invid=invid, imgid=imgid)
            return True
        except Exception as e:
            print(f"Error in adding images to inventory: {e}")
            return False
