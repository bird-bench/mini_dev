-- A comprehensive log of various events including meetings, games, and community service activities, with details on timing, location, and current status.
-- 42 rows, primary key: (event_id)
CREATE TABLE event (
-- A unique identifier for the event. Format: 'rec' followed by 15 alphanumeric characters.
-- Stats: 0% null 100% unique
-- Foreign keys: attendance.link_to_event (one-to-many), budget.link_to_event (one-to-many)
event_id text,
-- Name of the event
-- Stats: 0% null 92.9% unique
event_name text,
-- The date and time the event took place or is scheduled to take place. Format: YYYY-MM-DDTHH:MM:SS
-- Stats: 0% null 97.6% unique
event_date text,
-- The kind of event. Values include: 'Meeting', 'Guest Speaker', 'Game', 'Social', 'Community Service', 'Election', 'Budget', 'Registration'
-- Stats: 0% null 19% unique
type text,
-- Additional information about the event. May include details on attendance, eligibility, or activity description.
-- Stats: 52.4% null 35.7% unique
notes text,
-- Where the event was or will be held. Can be a specific room, building, address, or general area.
-- Stats: 14.3% null 28.6% unique
location text,
-- Current state of the event. Values: 'Open', 'Closed', or 'Planning'
-- Stats: 0% null 7.14% unique
status text
);
-- A comprehensive list of academic majors offered at a university, including their associated departments and colleges.
-- 113 rows, primary key: (major_id)
CREATE TABLE major (
-- A unique identifier for each major. Values follow the pattern 'rec' followed by alphanumeric characters.
-- Stats: 0% null 100% unique
-- Foreign keys: member.link_to_major (one-to-many)
major_id text,
-- The name of the academic major.
-- Stats: 0% null 100% unique
major_name text,
-- The name of the department that offers the major.
-- Stats: 0% null 41.6% unique
department text,
-- The name of the college that houses the department offering the major.
-- Stats: 0% null 7.08% unique
college text
);
-- Comprehensive US ZIP code database with geographical and administrative information.
-- 41877 rows, primary key: (zip_code)
CREATE TABLE zip_code (
-- Five-digit number identifying a US post office. Range: 501 to 99950.
-- Stats: 0% null 100% unique
-- Foreign keys: member.zip (one-to-one)
zip_code integer,
-- The kind of ZIP code. Values: 'Standard' (normal codes), 'PO Box' (post office boxes), 'Unique' (assigned to individual organizations).
-- Stats: 0% null 0.00716% unique
type text,
-- The city to which the ZIP pertains.
-- Stats: 0% null 44.7% unique
city text,
-- The county to which the ZIP pertains.
-- Stats: 0.21% null 4.8% unique
county text,
-- The name of the state to which the ZIP pertains.
-- Stats: 0% null 0.124% unique
state text,
-- Two-letter abbreviation of the state. See state.
-- Stats: 0% null 0.124% unique
short_state text
);
-- Records event attendance, linking events to members who attended
-- 326 rows, primary key: (link_to_event, link_to_member)
CREATE TABLE attendance (
-- Unique identifier referencing the Event table
-- Stats: 0% null 5.21% unique
-- Foreign keys: event.event_id (many-to-one)
link_to_event text,
-- Unique identifier referencing the Member table
-- Stats: 0% null 9.2% unique
-- Foreign keys: member.member_id (many-to-one)
link_to_member text
);
-- Tracks budget allocations, expenditures, and statuses for various event categories, linking to specific events.
-- 52 rows, primary key: (budget_id)
CREATE TABLE budget (
-- A unique identifier for the budget entry. Format: 'rec' followed by 16 alphanumeric characters.
-- Stats: 0% null 100% unique
-- Foreign keys: expense.link_to_budget (one-to-many)
budget_id text,
-- The area for which the amount is budgeted. Values include 'Food', 'Advertisement', 'Speaker Gifts', 'Parking', 'Club T-Shirts'.
-- Stats: 0% null 9.62% unique
category text,
-- The total amount spent in dollars for the budgeted category. Summarized from the Expense table. Range: $0.00 to $327.07.
-- Stats: 0% null 32.7% unique
spent real,
-- Amount budgeted minus amount spent, in dollars. If negative, cost has exceeded budget. Range: -$24.25 to $150.00.
-- Stats: 0% null 42.3% unique
remaining real,
-- The amount budgeted in dollars. Likely calculated as spent + remaining. Range: $10 to $350.
-- Stats: 0% null 17.3% unique
amount integer,
-- Status of the event. Values: 'Closed' (event finished, no changes), 'Open' (ongoing, values may change), 'Planning' (not started, no changes).
-- Stats: 0% null 5.77% unique
event_status text,
-- Unique identifier referencing the Event table. Format: 'rec' followed by 16 alphanumeric characters.
-- Stats: 0% null 44.2% unique
-- Foreign keys: event.event_id (many-to-one)
link_to_event text
);
-- Tracks detailed information about expenses including descriptions, dates, costs, approval status, and links to members and budget categories
-- 32 rows, primary key: (expense_id)
CREATE TABLE expense (
-- Unique identifier for each expense, format: 'rec' followed by 14 alphanumeric characters
-- Stats: 0% null 100% unique
expense_id text,
-- Brief description of the expense item
-- Stats: 0% null 37.5% unique
expense_description text,
-- Date the expense was incurred, format: YYYY-MM-DD
-- Stats: 0% null 53.1% unique
expense_date text,
-- Dollar amount of the expense, ranging from $6.00 to $295.12
-- Stats: 0% null 65.6% unique
cost real,
-- See value_description: true/ false
-- Stats: 3.12% null 3.12% unique
approved text,
-- Identifier of the member who incurred the expense, format similar to expense_id
-- Stats: 0% null 9.38% unique
-- Foreign keys: member.member_id (many-to-one)
link_to_member text,
-- References the Budget table, format similar to expense_id
-- Stats: 0% null 75% unique
-- Foreign keys: budget.budget_id (many-to-one)
link_to_budget text
);
-- A record of income transactions for an organization, including details such as amount, source, date, and associated member.
-- 36 rows, primary key: (income_id)
CREATE TABLE income (
-- A unique identifier for each income record. Format: 'rec' followed by 15 alphanumeric characters.
-- Stats: 0% null 100% unique
income_id text,
-- Date when the fund was received. Format: YYYY-MM-DD. Range: 2019-09-01 to 2019-10-31.
-- Stats: 0% null 80.6% unique
date_received text,
-- Amount of funds received in dollars. Values: 50, 200, 1000, 3000.
-- Stats: 0% null 11.1% unique
amount integer,
-- Origin of the funds. Values: 'Dues', 'Sponsorship', 'School Appropration', 'Fundraising'.
-- Stats: 0% null 11.1% unique
source text,
-- Additional details about the fund receipt. Examples: 'Secured donations to help pay for speaker gifts.', 'Annual funding from Student Government.'
-- Stats: 91.7% null 8.33% unique
notes text,
-- Reference to a member, possibly in another table. Format: 'rec' followed by 15 alphanumeric characters.
-- Stats: 8.33% null 86.1% unique
-- Foreign keys: member.member_id (many-to-one)
link_to_member text
);
-- Comprehensive member information for a club, including personal details, contact information, and club-related data
-- 33 rows, primary key: (member_id)
CREATE TABLE member (
-- Unique identifier for each member, format: 'rec' followed by 16 alphanumeric characters
-- Stats: 0% null 100% unique
-- Foreign keys: attendance.link_to_member (one-to-many), expense.link_to_member (one-to-many), income.link_to_member (one-to-many)
member_id text,
-- Member's first name
-- Stats: 0% null 100% unique
first_name text,
-- Member's last name. Full name is first_name + last_name, e.g., Angela Sanders
-- Stats: 0% null 100% unique
last_name text,
-- Member's email address, format: firstname.lastname@lpu.edu
-- Stats: 0% null 100% unique
email text,
-- Member's role in the club. Values include 'Member', 'Inactive', 'Vice President', 'Treasurer', 'Secretary', 'President'
-- Stats: 0% null 18.2% unique
position text,
-- Preferred t-shirt size. Values: 'Small', 'Medium', 'Large', 'X-Large'. Usually, larger sizes indicate bigger body shape
-- Stats: 0% null 12.1% unique
t_shirt_size text,
-- Member's contact phone number, format: XXX-XXX-XXXX or (XXX) XXX-XXXX
-- Stats: 0% null 100% unique
phone text,
-- Zip code of member's hometown, ranging from 1020 to 98290
-- Stats: 0% null 100% unique
-- Foreign keys: zip_code.zip_code (one-to-one)
zip integer,
-- Unique identifier referencing the Major table, format: 'rec' followed by 16 alphanumeric characters
-- Stats: 3.03% null 78.8% unique
-- Foreign keys: major.major_id (many-to-one)
link_to_major text
);