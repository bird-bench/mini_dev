-- This table contains detailed information about California schools, including enrollment, free and reduced-price meal eligibility, and various school characteristics for the 2014-2015 academic year.
-- 9986 rows, primary key: (CDSCode)
CREATE TABLE frpm (
-- 14-digit unique identifier for each school
-- Stats: 0% null 100% unique
-- Foreign keys: schools.CDSCode (one-to-one)
CDSCode text,
-- See Academic Year
-- Stats: 0% null 0.01% unique
"Academic Year" text,
-- 2-digit code representing the county
-- Stats: 0% null 0.581% unique
"County Code" text,
-- 5-digit code representing the district
-- Stats: 0% null 10.1% unique
"District Code" integer,
-- 7-digit code representing the school
-- Stats: 0% null 99.6% unique
"School Code" text,
-- Name of the county
-- Stats: 0% null 0.581% unique
"County Name" text,
-- Name of the school district
-- Stats: 0% null 10% unique
"District Name" text,
-- Name of the school
-- Stats: 0% null 86.6% unique
"School Name" text,
-- Type of school district (e.g., 'Unified School District', 'Elementary School District')
-- Stats: 0% null 0.0801% unique
"District Type" text,
-- Type of school (e.g., 'Elementary Schools (Public)', 'High Schools (Public)')
-- Stats: 0.451% null 0.17% unique
"School Type" text,
-- Educational option type (e.g., 'Traditional', 'Continuation School')
-- Stats: 0.451% null 0.12% unique
"Educational Option Type" text,
-- National School Lunch Program provision status (e.g., 'Provision 2', 'CEP')
-- Stats: 81.5% null 0.0701% unique
"NSLP Provision Status" text,
-- Indicates if the school is a charter school. 0: N; 1: Y
-- Stats: 0.451% null 0.02% unique
"Charter School (Y/N)" integer,
-- Unique identifier for charter schools
-- Stats: 88.3% null 11.5% unique
"Charter School Number" text,
-- Funding type for charter schools (e.g., 'Directly funded', 'Locally funded')
-- Stats: 88.3% null 0.03% unique
"Charter Funding Type" text,
-- Not useful
-- Stats: 0.451% null 0.02% unique
IRC integer,
-- Lowest grade level offered at the school
-- Stats: 0% null 0.15% unique
"Low Grade" text,
-- Highest grade level offered at the school
-- Stats: 0% null 0.17% unique
"High Grade" text,
-- Number of students enrolled in grades K-12
-- Stats: 0% null 18.8% unique
"Enrollment (K-12)" real,
-- Number of K-12 students eligible for free meals
-- Stats: 0.561% null 12.2% unique
"Free Meal Count (K-12)" real,
-- Percentage of K-12 students eligible for free meals (0-1 scale)
-- Stats: 0.561% null 86.7% unique
"Percent (%) Eligible Free (K-12)" real,
-- Number of K-12 students eligible for free or reduced-price meals
-- Stats: 0.501% null 13.6% unique
"FRPM Count (K-12)" real,
-- Percentage of K-12 students eligible for free or reduced-price meals (0-1 scale)
-- Stats: 0.501% null 86.4% unique
"Percent (%) Eligible FRPM (K-12)" real,
-- Number of students enrolled ages 5-17
-- Stats: 0.14% null 18.5% unique
"Enrollment (Ages 5-17)" real,
-- Number of students ages 5-17 eligible for free meals
-- Stats: 0.781% null 12.1% unique
"Free Meal Count (Ages 5-17)" real,
-- Percentage of students ages 5-17 eligible for free meals (0-1 scale)
-- Stats: 0.781% null 85.6% unique
"Percent (%) Eligible Free (Ages 5-17)" real,
-- Number of students ages 5-17 eligible for free or reduced-price meals
-- Stats: 0.721% null 13.3% unique
"FRPM Count (Ages 5-17)" real,
-- Percentage of students ages 5-17 eligible for free or reduced-price meals (0-1 scale)
-- Stats: 0.721% null 85.7% unique
"Percent (%) Eligible FRPM (Ages 5-17)" real,
-- Certification status for CALPADS Fall 1 data in 2013-14
-- Stats: 0% null 0.01% unique
"2013-14 CALPADS Fall 1 Certification Status" integer
);
-- California schools' SAT performance data, including enrollment, test-taker counts, and average scores for Reading, Math, and Writing sections
-- 2269 rows, primary key: (cds)
CREATE TABLE satscores (
-- 14-digit unique identifier for California Department Schools
-- Stats: 0% null 100% unique
-- Foreign keys: schools.CDSCode (one-to-one)
cds text,
-- Unuseful column with values 'S' or 'D'
-- Stats: 0% null 0.0881% unique
rtype text,
-- School name
-- Stats: 22.9% null 73.4% unique
sname text,
-- District name
-- Stats: 0% null 22.9% unique
dname text,
-- County name
-- Stats: 0% null 2.51% unique
cname text,
-- Total enrollment for grades 1-12, ranging from 0 to 43,324
-- Stats: 0% null 36.8% unique
enroll12 integer,
-- Number of SAT test takers in each school, ranging from 0 to 24,305
-- Stats: 0% null 24.1% unique
NumTstTakr integer,
-- Average SAT Reading score, ranging from 308 to 653
-- Stats: 26.3% null 11.9% unique
AvgScrRead integer,
-- Average SAT Math score, ranging from 289 to 699
-- Stats: 26.3% null 13% unique
AvgScrMath integer,
-- Average SAT Writing score, ranging from 312 to 671
-- Stats: 26.3% null 11.8% unique
AvgScrWrite integer,
-- Number of test takers with total SAT scores ≥ 1500. Can be used with NumTstTakr to calculate excellence rate
-- Stats: 26.3% null 16.2% unique
NumGE1500 integer
);
-- Comprehensive database of California schools including administrative, location, and operational details
-- 17686 rows, primary key: (CDSCode)
CREATE TABLE schools (
-- 14-digit unique identifier for each school
-- Stats: 0% null 100% unique
-- Foreign keys: frpm.CDSCode (one-to-one), satscores.cds (one-to-one)
CDSCode text,
-- 7-digit National Center for Educational Statistics school district identification number. First 2 digits identify state, last 5 identify district.
-- Stats: 5.82% null 6.75% unique
NCESDist text,
-- 5-digit NCES school identification number. Combined with NCESDist forms a unique 12-digit ID for each school.
-- Stats: 28.5% null 69.7% unique
NCESSchool text,
-- Status of the district. Values: Active, Closed, Merged, Pending.
-- Stats: 0% null 0.0226% unique
StatusType text,
-- County name
-- Stats: 0% null 0.328% unique
County text,
-- District name
-- Stats: 0% null 7.98% unique
District text,
-- School name
-- Stats: 7.74% null 78.5% unique
School text,
-- Street address
-- Stats: 1.66% null 76.9% unique
Street text,
-- Abbreviated street address. Some closed/retired schools may lack data.
-- Stats: 1.66% null 77.1% unique
StreetAbr text,
-- City name
-- Stats: 1.66% null 6.59% unique
City text,
-- Zip code
-- Stats: 1.66% null 63.2% unique
Zip text,
-- State abbreviation (CA)
-- Stats: 1.66% null 0.00565% unique
State text,
-- Unabbreviated mailing address. May be empty for closed/retired schools or filled with Street data if not provided.
-- Stats: 1.65% null 70.1% unique
MailStreet text,
-- See MailStreet
-- Stats: 1.65% null 70.3% unique
MailStrAbr text,
-- See City
-- Stats: 1.65% null 6.4% unique
MailCity text,
-- See Zip
-- Stats: 1.65% null 58.2% unique
MailZip text,
-- See State
-- Stats: 1.65% null 0.00565% unique
MailState text,
-- Phone number
-- Stats: 33.7% null 60.1% unique
Phone text,
-- Phone extension
-- Stats: 96.9% null 2.14% unique
Ext text,
-- Website address
-- Stats: 60.6% null 23.1% unique
Website text,
-- Date school opened (YYYY-MM-DD)
-- Stats: 7.74% null 7.95% unique
OpenDate date,
-- Date school closed (YYYY-MM-DD)
-- Stats: 67.8% null 5.08% unique
ClosedDate date,
-- Charter school indicator (1 = charter, 0 = not charter)
-- Stats: 7.74% null 0.0113% unique
Charter integer,
-- 4-digit charter school number
-- Stats: 89.8% null 9.97% unique
CharterNum text,
-- Charter school funding type: 'Directly funded', 'Locally funded', or 'Not in CS funding model'
-- Stats: 90.7% null 0.017% unique
FundingType text,
-- District Ownership Code. Numeric code for Administrative Authority category.
-- Stats: 0% null 0.0679% unique
DOC text,
-- Text description of DOC category
-- Stats: 0% null 0.0679% unique
DOCType text,
-- School Ownership Code. Numeric code for school type.
-- Stats: 7.74% null 0.113% unique
SOC text,
-- Text description of school type
-- Stats: 7.74% null 0.113% unique
SOCType text,
-- Short text description of education type offered
-- Stats: 32.3% null 0.0735% unique
EdOpsCode text,
-- Long text description of education type offered
-- Stats: 32.3% null 0.0735% unique
EdOpsName text,
-- Short code for institution type based on grade range
-- Stats: 7.74% null 0.0396% unique
EILCode text,
-- Long description of institution type based on grade range
-- Stats: 7.74% null 0.0396% unique
EILName text,
-- Grade span offered (lowest to highest grade)
-- Stats: 21.9% null 0.531% unique
GSoffered text,
-- Grade span served based on CALPADS Fall 1 data (K-12 only)
-- Stats: 32.5% null 0.458% unique
GSserved text,
-- Virtual instruction type: F (Exclusively), V (Primarily), C (Primarily Classroom), N (Not Virtual), P (Partial)
-- Stats: 38.8% null 0.017% unique
Virtual text,
-- Magnet school indicator (1 = magnet, 0 = not magnet)
-- Stats: 40% null 0.0113% unique
Magnet integer,
-- Latitude coordinate of school location
-- Stats: 27.3% null 64.7% unique
Latitude real,
-- Longitude coordinate of school location
-- Stats: 27.3% null 63.8% unique
Longitude real,
-- Administrator's first name
-- Stats: 33.8% null 13.2% unique
AdmFName1 text,
-- Administrator's last name
-- Stats: 33.8% null 36.2% unique
AdmLName1 text,
-- Administrator's email address
-- Stats: 34% null 59.3% unique
AdmEmail1 text,
-- See AdmFName1
-- Stats: 97.6% null 1.61% unique
AdmFName2 text,
-- See AdmLName1
-- Stats: 97.6% null 2.05% unique
AdmLName2 text,
-- See AdmEmail1
-- Stats: 97.6% null 2.16% unique
AdmEmail2 text,
-- Not useful
-- Stats: 99.8% null 0.226% unique
AdmFName3 text,
-- Not useful
-- Stats: 99.8% null 0.237% unique
AdmLName3 text,
-- Not useful
-- Stats: 99.8% null 0.237% unique
AdmEmail3 text,
-- Date of last record update (YYYY-MM-DD)
-- Stats: 0% null 4.28% unique
LastUpdate date
);