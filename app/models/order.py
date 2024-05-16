from flask import current_app as app
from .inventory import Inventory

class Order:
    def __init__(self, id, uid, time_created, fulfillment_status='pending', time_fulfilled=None):
        """Initialize a new Order instance with various attributes."""
        self.id = id
        self.uid = uid
        self.time_created = time_created
        self.fulfillment_status = fulfillment_status
        self.time_fulfilled = time_fulfilled


    # Get order information
    @staticmethod
    def getById(id):
        """Retrieve a single order by its ID."""
        rows = app.db.execute('''
            SELECT id, uid, time_created, fulfillment_status, time_fulfilled
            FROM Orders
            WHERE id = :id
            ''', id=id)
        return Order(*(rows[0])) if rows is not None else None
    
    
    @staticmethod
    def getByUser(uid): 
        """Retrieve all orders made by a specific user, sorted by order ID."""
        rows = app.db.execute('''
            SELECT id, uid, time_created, fulfillment_status, time_fulfilled
            FROM Orders
            WHERE uid = :uid
            ORDER BY id
            ''', uid=uid)
        return [Order(*row) for row in rows]
    
    
    @staticmethod
    def orderByFulfillmentStatus():
        """Retrieve orders sorted by fulfillment status and creation time using window functions."""
        rows = app.db.execute('''
            SELECT id, uid, time_created, fulfillment_status,
                ROW_NUMBER() OVER (
                    PARTITION BY fulfillment_status 
                    ORDER BY time_created DESC
                ) AS row_num
            FROM orders
            ORDER BY CASE fulfillment_status 
                    WHEN 'pending' THEN 1 
                    WHEN 'fulfilled' THEN 2 
                END
            ''')
        return [Order(*row) for row in rows]


    # Add order
    @staticmethod
    def add_new_order(uid, fulfillment_status='pending', time_fulfilled=None):
        """Add a new order to the database and return the order ID."""
        try:
            rows = app.db.execute("""
                INSERT INTO Orders(uid, fulfillment_status, time_fulfilled)
                VALUES(:uid, :fulfillment_status, :time_fulfilled)
                RETURNING id
                """,
                uid=uid,
                fulfillment_status=fulfillment_status,
                time_fulfilled=time_fulfilled
            )
            oid = rows[0][0] 
            print(f"order_id is: {oid}")
            return oid
        except Exception as e:
            print(str(e))
            return None
    
    
    @staticmethod
    def add_to_order(oid, invid, unit_price, quantity):
        """Add items to an existing order and handle quantity updates."""
        try:
            # Check if the (oid, invid) pair exists in the Order_Products table
            existing_row = app.db.execute("""
                SELECT quantity FROM Order_Products
                WHERE oid = :oid AND invid = :invid
            """, oid=oid, invid=invid)

            if existing_row:
                # If the pair exists, increment the quantity by 1
                updated_quantity = existing_row[0][0] + quantity
                app.db.execute("""
                    UPDATE Order_Products
                    SET quantity = :updated_quantity
                    WHERE oid = :oid AND invid = :invid
                """, updated_quantity=updated_quantity, oid=oid, invid=invid)
            else:
                # If the pair doesn't exist, insert a new record with quantity 1
                app.db.execute("""
                    INSERT INTO Order_Products (oid, invid, quantity, price, fulfillment_status)
                    VALUES (
                        :oid,
                        :invid,
                        :quantity,
                        :unit_price,
                        'pending'
                    )
                """, oid=oid, invid=invid, quantity=quantity, unit_price=unit_price)

            return True
        except Exception as e:
            print(f"Error adding to order: {e}")
            return False


    # Update order
    @staticmethod
    def check_order_products_fulfilled(oid):
        """Check if all products in an order are fulfilled."""
        try:
            rows = app.db.execute("""
                SELECT COUNT(*)
                FROM Order_Products
                WHERE oid = :oid AND fulfillment_status <> 'fulfilled'
                """,oid=oid)
            # If the count is 0, all products are fulfilled
            return rows[0][0] == 0
        except Exception as e:
            print(str(e))
            return False
        
        
    @staticmethod
    def update_order_status(oid):
        """Update the order status to 'fulfilled' if all products are fulfilled."""
        if Order.check_order_products_fulfilled(oid):
            try:
                app.db.execute("""
                    UPDATE Orders
                    SET fulfillment_status = 'fulfilled', time_fulfilled = NOW()
                    WHERE id = :oid
                    """,oid=oid)
                print("Order status updated to 'fulfilled'.")
                return True
            except Exception as e:
                print(str(e))
        return False
        
                
    @staticmethod
    def get_by_seller(sid):
        """Retrieve all orders for a specific seller."""
        column_names = ['order_id', 'user_id', 'address', 'total_quantity', 'status', 'created_at', 'fulfilled_at']
        rows = app.db.execute('''
            SELECT 
                o.id AS order_id, 
                o.uid AS user_id, 
                u.address AS address, 
                SUM(op.quantity) AS total_quantity, 
                o.fulfillment_status AS status, 
                o.time_created AS created_at, 
                o.time_fulfilled AS fulfilled_at
            FROM Orders o
            JOIN Order_Products op ON o.id = op.oid
            JOIN Inventories i ON op.invid = i.id
            JOIN Users u ON o.uid = u.id
            WHERE i.sid = :sid
            GROUP BY order_id, user_id, address, status, created_at, fulfilled_at
            ORDER BY created_at DESC
            ''',
            sid=sid)
        return [dict(zip(column_names, row)) for row in rows] if rows else None
      
    
    @staticmethod
    def mark_as_fulfilled(oid, invid):
        """Mark a specific order product as fulfilled using both order ID and inventory ID."""
        try:
            result = app.db.execute("""
                UPDATE Order_Products
                SET fulfillment_status = 'fulfilled', time_fulfilled = NOW()
                WHERE oid = :oid AND invid = :invid AND fulfillment_status <> 'fulfilled'
                """, oid=oid, invid=invid)
            return True
        except Exception as e:
            print(f"Failed to mark order product as fulfilled: {e}")
            return False


    @staticmethod
    def get_order_products_by_seller(oid, sid):
        """Organizes order products by order ID into a dictionary and filters them by seller ID after retrieval."""
        all_products = Inventory.get_order_products(oid)
        
        # Filter products for the current seller
        filtered_products = [product for product in all_products if product['sid'] == sid] if all_products else []
        return filtered_products


    @staticmethod
    def get_all_order_products_by_seller(sid):
        """Organizes all order products into a dictionary and filters them by seller ID after retrieval."""
        all_products_all_order = Inventory.get_all_order_products(sid)
        
        # Filter products for the current seller
        filtered_products = [product for product in all_products_all_order] if all_products_all_order else []
        return filtered_products
    
    
    @staticmethod
    def search_by_criteria(uid, sid=None, order_id=None, start_date=None, end_date=None, inventory_name=None, role='seller'):
        """Search specific order history by criteria"""
        column_names = ['order_id', 'user_id', 'first_name', 'last_name', 'address', 'total_quantity', 'status', 'created_at', 'fulfilled_at', 'design_name', 'design_description']
        query = '''
            SELECT 
                o.id AS order_id, 
                o.uid AS user_id, 
                u.firstname AS first_name,
                u.lastname AS last_name,
                u.address AS address,
                SUM(op.quantity) AS total_quantity, 
                o.fulfillment_status AS status,
                o.time_created AS created_at, 
                o.time_fulfilled AS fulfilled_at,
                STRING_AGG(DISTINCT id.name, ', ') AS design_name,
                STRING_AGG(DISTINCT id.description, ', ') AS design_description
            FROM Orders o
            JOIN Order_Products op ON o.id = op.oid
            JOIN Inventories i ON op.invid = i.id
            JOIN Products p ON i.pid = p.id
            JOIN Users u ON o.uid = u.id
            LEFT JOIN Inventory_Designs id ON i.id = id.invid
        '''
        params = {'uid': uid}
        
        # Add criterias
        if role == 'seller':
            query += ' WHERE u.id <> :uid'
        else:
            query += ' WHERE u.id = :uid'

        if sid:
            query += ' AND i.sid = :sid'
            params['sid'] = sid
        if order_id:
            query += ' AND o.id = :order_id'
            params['order_id'] = order_id
        if start_date and end_date:
            query += ' AND o.time_created BETWEEN :start_date AND :end_date'
            params['start_date'] = start_date
            params['end_date'] = end_date
        if inventory_name:
            query += ''' AND (LOWER(p.name) LIKE :inventory_name
                     OR (id.name IS NOT NULL AND LOWER(id.name) LIKE :inventory_name))'''
            params['inventory_name'] = f'%{inventory_name}%'

        query += ' GROUP BY order_id, user_id, first_name, last_name, address, status, created_at, fulfilled_at ORDER BY created_at DESC'

        rows = app.db.execute(query, **params)
        return [dict(zip(column_names, row)) for row in rows]
    
    
    @staticmethod
    def get_order_history_with_summary(order_ids):
        """Get order history summary of specific orders"""
        column_names = ['order_id', 'total_amount', 'total_items']
        result = {}
        
        for oid in order_ids:
            query = '''
                SELECT
                    o.id AS order_id,
                    SUM(op.quantity * op.price) AS total_amount,
                    SUM(op.quantity) AS total_items
                FROM Orders o
                JOIN Order_Products op ON o.id = op.oid
                WHERE o.id = :oid
                GROUP BY o.id
            '''
            rows = app.db.execute(query, oid=oid)
            if rows:
                result[oid] = [dict(zip(column_names, row)) for row in rows][0]
        return result


    # Get order history stats
    @staticmethod
    def get_all_order(uid):
        """Get all orders with their order products summary"""
        column_names = ['order_id', 'user_id', 'first_name', 'last_name', 'address', 'total_quantity', 'status', 'created_at', 'fulfilled_at', 'design_name', 'design_description']
        query = '''
            SELECT 
                o.id AS order_id, 
                o.uid AS user_id, 
                u.firstname AS first_name,
                u.lastname AS last_name,
                u.address AS address,
                SUM(op.quantity) AS total_quantity, 
                o.fulfillment_status AS status,
                o.time_created AS created_at, 
                o.time_fulfilled AS fulfilled_at,
                STRING_AGG(DISTINCT id.name, ', ') AS design_name,
                STRING_AGG(DISTINCT id.description, ', ') AS design_description
            FROM Orders o
            JOIN Order_Products op ON o.id = op.oid
            JOIN Inventories i ON op.invid = i.id
            JOIN Products p ON i.pid = p.id
            JOIN Users u ON o.uid = u.id
            LEFT JOIN Inventory_Designs id ON i.id = id.invid
        '''
        params = {'uid': uid}
        
        query += ' GROUP BY order_id, user_id, first_name, last_name, address, status, created_at, fulfilled_at ORDER BY created_at DESC'

        rows = app.db.execute(query, **params)
        return [dict(zip(column_names, row)) for row in rows]
    

    @staticmethod
    def search_by_category(uid, category=None, role='seller'):
        """Search specific order history by category"""
        column_names = ['order_id', 'user_id', 'first_name', 'last_name', 'address', 'total_quantity', 'status', 'created_at', 'fulfilled_at', 'design_name', 'design_description']
        query = '''
            SELECT 
                o.id AS order_id, 
                o.uid AS user_id, 
                u.firstname AS first_name,
                u.lastname AS last_name,
                u.address AS address,
                SUM(op.quantity) AS total_quantity, 
                o.fulfillment_status AS status,
                o.time_created AS created_at, 
                o.time_fulfilled AS fulfilled_at,
                STRING_AGG(DISTINCT id.name, ', ') AS design_name,
                STRING_AGG(DISTINCT id.description, ', ') AS design_description
            FROM Orders o
            JOIN Order_Products op ON o.id = op.oid
            JOIN Inventories i ON op.invid = i.id
            JOIN Products p ON i.pid = p.id
            JOIN Tags t ON t.pid = p.id
            JOIN Categories cat ON cat.id = t.cid
            JOIN Users u ON o.uid = u.id
            LEFT JOIN Inventory_Designs id ON i.id = id.invid
        '''
        params = {'uid': uid}
        
        if role == 'seller':
            query += ' WHERE u.id <> :uid'
        else:
            query += ' WHERE u.id = :uid'

        if category and category != "All Categories":
            query += ''' AND cat.label LIKE :category'''
            params['category'] = f'%{category}%'

        query += ' GROUP BY order_id, user_id, first_name, last_name, address, status, created_at, fulfilled_at ORDER BY created_at DESC'

        rows = app.db.execute(query, **params)
        return [dict(zip(column_names, row)) for row in rows]
    