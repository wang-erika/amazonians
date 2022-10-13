\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);
\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(pid)+1 FROM Inventory),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(pid)+1 FROM Purchases),
                         false);

\COPY Sellers FROM 'Sellers.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Sellers),
                         false);

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(pid)+1 FROM Cart),
                         false);

\COPY RatesSeller FROM 'RatesSeller.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(uid)+1 FROM RatesSeller),
                         false);

\COPY RatesProduct FROM 'RatesProduct.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(pid)+1 FROM RatesProduct),
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(orid)+1 FROM Orders),
                         false);

\COPY RatesSeller FROM 'RatesSeller.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(uid)+1 FROM RatesSeller),
                         false);

\COPY RatesProduct FROM 'RatesProduct.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(pid)+1 FROM RatesProduct),
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(orid)+1 FROM Sellers),
                         false);