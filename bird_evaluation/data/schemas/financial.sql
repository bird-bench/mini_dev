-- Banking account information including identifiers, branch locations, issuance frequencies, and creation dates
-- 4500 rows, primary key: (account_id)
CREATE TABLE account (
-- Unique identifier for the account, ranging from 1 to 11382
-- Stats: 0% null 100% unique
-- Foreign keys: disp.account_id (one-to-many), loan.account_id (one-to-one), "order".account_id (one-to-many), trans.account_id (one-to-many)
account_id integer,
-- Branch location identifier, ranging from 1 to 77
-- Stats: 0% null 1.71% unique
-- Foreign keys: district.district_id (many-to-one)
district_id integer,
-- Account issuance frequency. 'POPLATEK MESICNE' stands for monthly issuance, 'POPLATEK TYDNE' for weekly issuance, and 'POPLATEK PO OBRATU' for issuance after transaction
-- Stats: 0% null 0.0667% unique
frequency text,
-- Account creation date in YYMMDD format, ranging from 1993-01-01 to 1997-12-29
-- Stats: 0% null 34.1% unique
"date" date
);
-- Credit card information including card details, type, and issuance date
-- 892 rows, primary key: (card_id)
CREATE TABLE card (
-- Unique identifier for credit cards, ranging from 1 to 1247
-- Stats: 0% null 100% unique
card_id integer,
-- Unique disposition identifier, ranging from 9 to 13660
-- Stats: 0% null 100% unique
-- Foreign keys: disp.disp_id (one-to-one)
disp_id integer,
-- Type of credit card. Values: 'junior' (junior class), 'classic' (standard class), 'gold' (high-level)
-- Stats: 0% null 0.336% unique
type text,
-- Date when the credit card was issued, in YYMMDD format. Range: '1993-11-07' to '1998-12-29'
-- Stats: 0% null 68% unique
issued date
);
-- Contains demographic information about clients, including their unique identifier, gender, birth date, and associated branch location
-- 5369 rows, primary key: (client_id)
CREATE TABLE client (
-- Unique identifier for clients, ranging from 1 to 13998
-- Stats: 0% null 100% unique
-- Foreign keys: disp.client_id (one-to-one)
client_id integer,
-- Client's gender: 'F' for female, 'M' for male
-- Stats: 0% null 0.0373% unique
gender text,
-- Client's birth date, ranging from '1911-08-20' to '1987-09-27'
-- Stats: 0% null 88.2% unique
birth_date date,
-- Branch location identifier, ranging from 1 to 77
-- Stats: 0% null 1.43% unique
-- Foreign keys: district.district_id (many-to-one)
district_id integer
);
-- Records of client dispositions for bank accounts, including ownership and usage rights
-- 5369 rows, primary key: (disp_id)
CREATE TABLE disp (
-- Unique identifier for each disposition record, ranging from 1 to 13690
-- Stats: 0% null 100% unique
-- Foreign keys: card.disp_id (one-to-one)
disp_id integer,
-- Unique identifier for each client, ranging from 1 to 13998
-- Stats: 0% null 100% unique
-- Foreign keys: client.client_id (one-to-one)
client_id integer,
-- Identifier for the associated account, ranging from 1 to 11382
-- Stats: 0% null 83.8% unique
-- Foreign keys: account.account_id (many-to-one)
account_id integer,
-- Type of disposition. Values are 'OWNER' or 'DISPONENT'. DISPONENT can only issue permanent orders or apply for loans
-- Stats: 0% null 0.0373% unique
type text
);
-- Comprehensive district-level data for Czech Republic, including demographics, economic indicators, and crime statistics
-- 77 rows, primary key: (district_id)
CREATE TABLE district (
-- Unique identifier for each district, ranging from 1 to 77
-- Stats: 0% null 100% unique
-- Foreign keys: account.district_id (one-to-many), client.district_id (one-to-many)
district_id integer,
-- Name of the district
-- Stats: 0% null 100% unique
A2 text,
-- Region where the district is located
-- Stats: 0% null 10.4% unique
A3 text,
-- Number of inhabitants in the district
-- Stats: 0% null 100% unique
A4 text,
-- Number of municipalities in the district with less than 499 inhabitants
-- Stats: 0% null 68.8% unique
A5 text,
-- Number of municipalities in the district with 500-1999 inhabitants
-- Stats: 0% null 46.8% unique
A6 text,
-- Number of municipalities in the district with 2000-9999 inhabitants
-- Stats: 0% null 22.1% unique
A7 text,
-- Number of municipalities in the district with more than 10000 inhabitants
-- Stats: 0% null 7.79% unique
A8 integer,
-- Not useful
-- Stats: 0% null 14.3% unique
A9 integer,
-- Ratio of urban inhabitants in the district, ranging from 33.9 to 100.0
-- Stats: 0% null 90.9% unique
A10 real,
-- Average salary in the district
-- Stats: 0% null 98.7% unique
A11 integer,
-- Unemployment rate in 1995, ranging from 0.2 to 7.3
-- Stats: 1.3% null 53.2% unique
A12 real,
-- Unemployment rate in 1996, ranging from 0.43 to 9.4
-- Stats: 0% null 94.8% unique
A13 real,
-- Number of entrepreneurs per 1000 inhabitants in the district
-- Stats: 0% null 57.1% unique
A14 integer,
-- Number of committed crimes in 1995
-- Stats: 1.3% null 97.4% unique
A15 integer,
-- Number of committed crimes in 1996
-- Stats: 0% null 98.7% unique
A16 integer
);
-- Loan data including loan details, account information, and repayment status
-- 682 rows, primary key: (loan_id)
CREATE TABLE loan (
-- Unique identifier for each loan, ranging from 4959 to 7308
-- Stats: 0% null 100% unique
loan_id integer,
-- Unique identifier for each account, ranging from 2 to 11362
-- Stats: 0% null 100% unique
-- Foreign keys: account.account_id (one-to-one)
account_id integer,
-- Date of loan approval, ranging from '1993-07-05' to '1998-12-08'
-- Stats: 0% null 82% unique
"date" date,
-- Approved loan amount in US dollars, ranging from $4,980 to $590,820
-- Stats: 0% null 94.6% unique
amount integer,
-- Loan duration in months. Possible values: 12, 24, 36, 48, 60
-- Stats: 0% null 0.733% unique
duration integer,
-- Monthly payment amount in US dollars, ranging from $304.0 to $9910.0
-- Stats: 0% null 84.6% unique
payments real,
-- Repayment status. 'A': contract finished, no problems; 'B': contract finished, loan not paid; 'C': running contract, OK so far; 'D': running contract, client in debt
-- Stats: 0% null 0.587% unique
status text
);
-- Transaction details including order ID, account information, amount, and payment purpose
-- 6471 rows, primary key: (order_id)
CREATE TABLE "order" (
-- Unique identifier for each order, ranging from 29401 to 46338
-- Stats: 0% null 100% unique
order_id integer,
-- Account identifier, ranging from 1 to 11362
-- Stats: 0% null 58.1% unique
-- Foreign keys: account.account_id (many-to-one)
account_id integer,
-- Two-letter code representing the recipient's bank (e.g., 'QR', 'YZ', 'AB')
-- Stats: 0% null 0.201% unique
bank_to text,
-- Recipient's account number. Each bank has a unique two-letter code. Values range from 399 to 99994199
-- Stats: 0% null 99.6% unique
account_to integer,
-- Debited amount in currency units, ranging from 1.0 to 14882.0
-- Stats: 0% null 68.2% unique
amount real,
-- Purpose of the payment. Values: 'POJISTNE' (insurance), 'SIPO' (household), 'LEASING', 'UVER' (loan), or empty string
-- Stats: 0% null 0.0773% unique
k_symbol text
);
-- Comprehensive transaction log for bank accounts, including transaction details, amounts, balances, and partner information
-- 1056320 rows, primary key: (trans_id)
CREATE TABLE trans (
-- Unique identifier for each transaction, ranging from 1 to 3,682,987
-- Stats: 0% null 100% unique
trans_id integer,
-- Identifier for the account, ranging from 1 to 11,382
-- Stats: 0% null 0.426% unique
-- Foreign keys: account.account_id (many-to-one)
account_id integer,
-- Date of transaction, ranging from '1993-01-01' to '1998-12-31'
-- Stats: 0% null 0.207% unique
"date" date,
-- Transaction type. 'PRIJEM' stands for credit, 'VYDAJ' stands for withdrawal
-- Stats: 0% null 0.000284% unique
type text,
-- Mode of transaction. 'VYBER KARTOU': credit card withdrawal, 'VKLAD': credit in cash, 'PREVOD Z UCTU': collection from another bank, 'VYBER': withdrawal in cash, 'PREVOD NA UCET': remittance to another bank
-- Stats: 17.3% null 0.000473% unique
operation text,
-- Amount of money in USD, ranging from 0 to 87,400
-- Stats: 0% null 3.4% unique
amount integer,
-- Balance after transaction in USD, ranging from -41,126 to 209,637
-- Stats: 0% null 10.5% unique
balance integer,
-- Characterization of the transaction. 'POJISTNE': insurance payment, 'SLUZBY': payment for statement, 'UROK': interest credited, 'SANKC. UROK': sanction interest if negative balance, 'SIPO': household, 'DUCHOD': old-age pension, 'UVER': loan payment
-- Stats: 45.6% null 0.000757% unique
k_symbol text,
-- Bank of the partner. Each bank has a unique two-letter code, ranging from 'AB' to 'YZ'
-- Stats: 74.1% null 0.00123% unique
bank text,
-- Account of the partner, ranging from 0 to 99,994,199
-- Stats: 72% null 0.726% unique
account integer
);