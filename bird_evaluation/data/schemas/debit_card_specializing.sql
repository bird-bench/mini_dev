-- Customer information table containing unique identifiers, client segments, and associated currencies.
-- 32461 rows, primary key: (CustomerID)
CREATE TABLE customers (
-- Unique identifier for each customer. Integer values ranging from 3 to 53314.
-- Stats: 0% null 100% unique
-- Foreign keys: yearmonth.CustomerID (one-to-many)
CustomerID integer,
-- Client segment categorization. Possible values are 'SME', 'LAM', and 'KAM'.
-- Stats: 0% null 0.00924% unique
Segment text,
-- Currency used by the customer. Can be either 'CZK' (Czech Koruna) or 'EUR' (Euro).
-- Stats: 0% null 0.00616% unique
Currency text
);
-- Gas stations data including identifiers, country, and market segment
-- 5716 rows, primary key: (GasStationID)
CREATE TABLE gasstations (
-- Unique identifier for each gas station, ranging from 44 to 5772
-- Stats: 0% null 100% unique
GasStationID integer,
-- Identifier for the chain the gas station belongs to, ranging from 1 to 290
-- Stats: 0% null 4.08% unique
ChainID integer,
-- Three-letter country code. Sample values: 'CZE' (Czech Republic), 'SVK' (Slovakia)
-- Stats: 0% null 0.035% unique
Country text,
-- Category of the gas station chain. Sample values: 'Other', 'Premium', 'Noname', 'Value for money', 'Discount'
-- Stats: 0% null 0.0875% unique
Segment text
);
-- A product catalog containing unique identifiers and descriptions for various items and services
-- 591 rows, primary key: (ProductID)
CREATE TABLE products (
-- Unique identifier for products, ranging from 1 to 630
-- Stats: 0% null 100% unique
ProductID integer,
-- Product description or name, includes various items and services in multiple languages (e.g., 'Servisní poplatek', 'Service charge', 'Potraviny')
-- Stats: 0% null 89.5% unique
Description text
);
-- Gas station transaction data including customer, product, and pricing information over a 4-day period in August 2012
-- 1000 rows, primary key: (TransactionID)
CREATE TABLE transactions_1k (
-- Unique identifier for each transaction, ranging from 1 to 1000
-- Stats: 0% null 100% unique
TransactionID integer,
-- Transaction date, ranging from '2012-08-23' to '2012-08-26'
-- Stats: 0% null 0.4% unique
"Date" date,
-- Transaction time, ranging from '00:07:00' to '23:20:00'
-- Stats: 0% null 59.9% unique
"Time" text,
-- Unique identifier for customers, ranging from 96 to 49838
-- Stats: 0% null 51.7% unique
CustomerID integer,
-- Unique identifier for payment cards, ranging from 26228 to 775970
-- Stats: 0% null 90.2% unique
CardID integer,
-- Unique identifier for gas stations, ranging from 48 to 5481
-- Stats: 0% null 43.7% unique
GasStationID integer,
-- Identifier for products purchased, ranging from 2 to 352
-- Stats: 0% null 2.8% unique
ProductID integer,
-- Quantity of product purchased, ranging from 0 to 264
-- Stats: 0% null 8.3% unique
Amount integer,
-- Total price of the transaction. Note: total price = Amount x Price. Values range from 1.76 to 5762.49
-- Stats: 0% null 93% unique
Price real
);
-- Monthly energy consumption data for customers over a two-year period.
-- 383282 rows, primary key: (CustomerID, Date)
CREATE TABLE yearmonth (
-- Unique identifier for customers. Integer values ranging from 5 to 52353.
-- Stats: 0% null 7.97% unique
-- Foreign keys: customers.CustomerID (many-to-one)
CustomerID integer,
-- Year and month in YYYYMM format. Ranges from '201112' to '201311'.
-- Stats: 0% null 0.00548% unique
"Date" text,
-- Monthly energy consumption in unknown units. Ranges from -582092.86 to 2052187.11, with both positive and negative values.
-- Stats: 0% null 72.8% unique
Consumption real
);