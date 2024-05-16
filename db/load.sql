\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.carts_id_seq',
                         (SELECT MAX(id)+1 FROM Carts),
                         false);

\COPY Images FROM 'Images.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.images_id_seq',
                         (SELECT MAX(id)+1 FROM Images),
                         false);

\COPY Categories FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.categories_id_seq',
                         (SELECT MAX(id)+1 FROM Categories),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

                         
\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.sellers_id_seq',
                         (SELECT MAX(id)+1 FROM Sellers),
                         false);

\COPY Tags FROM 'Tags.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Inventories FROM 'Inventories.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.inventories_id_seq',
                         (SELECT MAX(id)+1 FROM Inventories),
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                         (SELECT MAX(id)+1 FROM Orders),
                         false);

\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.reviews_id_seq',
                         (SELECT MAX(id)+1 FROM Reviews),
                         false);

\COPY Feedbacks FROM 'Feedbacks.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.feedbacks_id_seq',
                         (SELECT MAX(id)+1 FROM Feedbacks),
                         false);

\COPY Order_Products FROM 'Order_Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Cart_Products FROM 'Cart_Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Inventory_Designs FROM 'Inventory_Designs.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Inventory_Images FROM 'Inventory_Images.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Feedback_Images FROM 'Feedback_Images.csv' WITH DELIMITER ',' NULL '' CSV
\COPY Review_Images FROM 'Review_Images.csv' WITH DELIMITER ',' NULL '' CSV