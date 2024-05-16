from flask import current_app as app
from .image import Image
from .inventory import Inventory

class Product:
    """Class for product management with methods for CRUD operations related to product data."""

    def __init__(self, id, uid, name, description, imgid):
        """
        Initializes a new Product instance.
        Args:
            id (int): Product ID.
            uid (int): User ID of the product creator or owner.
            name (str): Name of the product.
            description (str): Description of the product.
        """
        self.id = id
        self.uid = uid
        self.name = name
        self.description = description
        self.imgid = imgid


    @staticmethod
    def get(id):
        """Retrieve a product by its ID.
        Args:
            id (int): The product ID to search for.
        Returns:
            Product: A Product instance if found, else None.
        """
        rows = app.db.execute('''
            SELECT id, uid, name, description, imgid
            FROM Products
            WHERE id = :id
            ''', id=id)
        return Product(*(rows[0])) if rows else None


    @staticmethod
    def get_all():
        """Retrieve all products.
        Returns:
            List[Product]: A list of all Product instances from the database.
        """
        rows = app.db.execute('''
            SELECT id, uid, name, description, imgid
            FROM Products
            ORDER BY name
            ''')
        return [Product(*row) for row in rows]
    
    
    @staticmethod
    def get_inventory_products(invid):
        """Retrieve the product associated with a specific inventory ID.
        Args:
            invid (int): Inventory ID to find the associated product.
        Returns:
            Product: A Product instance if found, else None.
        """
        rows = app.db.execute('''
            SELECT p.id, p.uid, p.name, p.description, p.imgid
            FROM products p
            JOIN inventories i ON p.id = i.pid
            WHERE i.id = :invid
            ''', invid=invid)
        return Product(*(rows[0])) if rows else None
    
    
    @staticmethod
    def add_new_product(uid, name, description, file, sid, current_quantity, price):
        """Add a new product and its inventory to the database along with an image."""
        try:
            imgid = Image.add_image(file).id
            if imgid:
                result = app.db.execute('''
                    INSERT INTO Products (uid, name, description, imgid)
                    VALUES (:uid, :name, :description, :imgid)
                    RETURNING id
                ''', uid=uid, name=name, description=description, imgid=imgid)
                
                new_product_id = result[0][0]
                
                if new_product_id:
                    inventory = Inventory.addNewInventory(sid, new_product_id, current_quantity, price)
                    if inventory:
                        return {'product': Product.get(new_product_id), 'inventory': inventory} 
            return None
        except Exception as e:
            print(f"Error adding new product: {e}")
            return None
    
    
    @staticmethod
    def update_product(pid, name, description):
        """Update product information."""
        try:        
            update_query = '''
                UPDATE Products
                SET name = :name, description = :description
                WHERE id = :pid
                RETURNING id
            '''
            update_params = {'name': name, 'description': description, 'pid': pid}
            result = app.db.execute(update_query, **update_params)
            if result:
                return Product.get(pid)
            else:
                return None
        except Exception as e:
            print(f"Error updating product: {e}")
            return None
