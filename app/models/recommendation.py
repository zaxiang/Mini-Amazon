from flask import current_app as app

class Recommendation:

    @staticmethod
    def recommend_products_based_on_history_and_reviews(user_id):
        """
        Recommends top 3 inventories based on user's most frequently purchased categories and high-rated reviews, excluding the user's own products.
        Incorporates inventory design if available.
        """
        column_names = ['inventory_id', 'product_name', 'display_name', 'display_description', 'image_id', 'current_quantity', 'price', 'sales_count', 'avg_rating', 'category_label']

        query = """
        WITH UserTopCategories AS (
            SELECT t.cid, COUNT(*) AS category_count
            FROM Orders o
            JOIN Order_Products op ON o.id = op.oid
            JOIN Inventories i ON op.invid = i.id
            JOIN Tags t ON i.pid = t.pid
            WHERE o.uid = :user_id
            GROUP BY t.cid
            ORDER BY category_count DESC
            LIMIT 5
        ), CategorySales AS (
            SELECT 
                i.id AS inventory_id, 
                i.pid,
                t.cid,
                COUNT(op.oid) AS sales_count, 
                COALESCE(AVG(r.rating), 0) AS avg_rating 
            FROM 
                Inventories i
            JOIN Tags t ON i.pid = t.pid
            JOIN Order_Products op ON i.id = op.invid
            LEFT JOIN Reviews r ON i.id = r.invid
            WHERE 
                t.cid IN (SELECT cid FROM UserTopCategories) 
            GROUP BY 
                i.id, i.pid, t.cid
        ), RankedProducts AS (
            SELECT
                cs.inventory_id AS inventory_id,
                p.name AS product_name,
                COALESCE(id.name, p.name) AS display_name,
                COALESCE(id.description, p.description) AS display_description,
                p.imgid AS image_id, 
                i.current_quantity AS current_quantity,
                i.price AS price,
                cs.sales_count AS sales_count,
                cs.avg_rating AS avg_rating,
                c.label AS category_label
            FROM 
                CategorySales cs
            JOIN Inventories i ON cs.inventory_id = i.id
            JOIN Products p ON i.pid = p.id
            LEFT JOIN Inventory_Designs id ON i.id = id.invid
            JOIN Categories c ON cs.cid = c.id
            WHERE 
                i.id NOT IN (
                    SELECT invid FROM Order_Products WHERE oid IN (
                        SELECT id FROM Orders WHERE uid = :user_id
                    )
                ) AND i.id NOT IN (
                    SELECT invid FROM Cart_Products WHERE cid = (
                        SELECT id FROM Carts WHERE uid = :user_id
                    )
                ) AND i.sid != :user_id
            ORDER BY 
                cs.sales_count DESC, cs.avg_rating DESC 
            LIMIT 10
        )
        SELECT 
                DISTINCT inventory_id,
                product_name,
                display_name,
                display_description,
                image_id,
                current_quantity,
                price,
                sales_count,
                avg_rating,
                category_label
        FROM RankedProducts;
        """
        rows = app.db.execute(query, user_id=user_id)
        return [dict(zip(column_names, row)) for row in rows] if rows else None