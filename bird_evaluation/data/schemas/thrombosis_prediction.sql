-- Medical examination data including patient ID, examination date, various antibody concentrations, diagnoses, coagulation measures, symptoms, and thrombosis severity
-- 106 rows
CREATE TABLE Examination (
-- Patient identification number ranging from 14872 to 5779550
-- Stats: 34% null 65.1% unique
-- Foreign keys: Patient.ID (many-to-one)
ID integer,
-- Date of examination in YYYY-MM-DD format, ranging from 1992-07-20 to 1998-04-02
-- Stats: 3.77% null 88.7% unique
"Examination Date" date,
-- Anti-Cardiolipin antibody (IgG) concentration, ranging from 0.0 to 2150.3
-- Stats: 0% null 31.1% unique
"aCL IgG" real,
-- Anti-Cardiolipin antibody (IgM) concentration, ranging from 0.0 to 200.0
-- Stats: 0% null 46.2% unique
"aCL IgM" real,
-- Anti-nucleus antibody concentration, with values 0, 4, 16, 64, 256, 1024, 4096
-- Stats: 17.9% null 6.6% unique
ANA integer,
-- Pattern observed in ANA examination sheet. Values include 'S', 'P', 'P,S', 'S,P', 'S,D', 'D,P,S'
-- Stats: 38.7% null 5.66% unique
"ANA Pattern" text,
-- Anti-Cardiolipin antibody (IgA) concentration, ranging from 0 to 223
-- Stats: 0% null 19.8% unique
"aCL IgA" integer,
-- Disease names, including 'SLE', 'SjS', 'RA', 'Behcet', 'APS', 'SLE, SjS', 'PSS', 'MCTD', 'collagen disease', 'brain infarction'
-- Stats: 22.6% null 41.5% unique
Diagnosis text,
-- Measure of degree of coagulation. '+': positive, '-': negative
-- Stats: 80.2% null 1.89% unique
KCT text,
-- See KCT
-- Stats: 80.2% null 1.89% unique
RVVT text,
-- See KCT
-- Stats: 76.4% null 1.89% unique
LAC text,
-- Other symptoms observed, such as 'CNS lupus', 'Apo', 'thrombophlebitis', 'thrombocytopenia', 'brain infarction'
-- Stats: 88.7% null 9.43% unique
Symptoms text,
-- Degree of thrombosis. 0: negative (no thrombosis), 1: positive (most severe), 2: positive (severe), 3: positive (mild)
-- Stats: 0% null 3.77% unique
Thrombosis integer
);
-- Patient medical records including demographics, admission details, and diagnoses
-- 1238 rows, primary key: (ID)
CREATE TABLE Patient (
-- Unique patient identifier ranging from 2110 to 5845877
-- Stats: 0% null 100% unique
-- Foreign keys: Examination.ID (one-to-many), Laboratory.ID (one-to-many)
ID integer,
-- Patient's sex. Values: 'F' (female), 'M' (male), or empty
-- Stats: 0% null 0.242% unique
SEX text,
-- Patient's date of birth in YYYY-MM-DD format, ranging from 1912-08-28 to 2007-05-28
-- Stats: 0.0808% null 96.4% unique
Birthday date,
-- First date when patient data was recorded in YYYY-MM-DD format. Null or empty if not recorded
-- Stats: 17.4% null 7.84% unique
Description date,
-- Date when patient first came to the hospital in YYYY-MM-DD format, ranging from 1972-08-02 to 1998-08-28
-- Stats: 20.3% null 64.4% unique
"First Date" date,
-- Patient admission status. '+': admitted to hospital, '-': followed at outpatient clinic. Also includes empty and '+('' values
-- Stats: 0% null 0.323% unique
Admission text,
-- Disease names. Examples include 'SLE', 'SJS', 'RA', 'BEHCET', 'PSS'
-- Stats: 0% null 17.8% unique
Diagnosis text
);
-- Laboratory test results for patients, including various blood and immunological markers
-- 13908 rows, primary key: (ID, Date)
CREATE TABLE Laboratory (
-- Patient identification number, ranging from 27654 to 5452747
-- Stats: 0% null 2.17% unique
-- Foreign keys: Patient.ID (many-to-one)
ID integer,
-- Date of laboratory tests in YYMMDD format, ranging from 1981-01-27 to 1999-03-04
-- Stats: 0% null 26.8% unique
"Date" date,
-- AST glutamic oxaloacetic transaminase. Normal range: N < 60. Values range from 3 to 21480
-- Stats: 18.9% null 1.57% unique
GOT integer,
-- ALT glutamic pyruvic transaminase. Normal range: N < 60. Values range from 1 to 4780
-- Stats: 18.9% null 2.17% unique
GPT integer,
-- Lactate dehydrogenase. Normal range: N < 500. Values range from 25 to 67080
-- Stats: 18.7% null 6.59% unique
LDH integer,
-- Alkaliphophatase. Normal range: N < 300. Values range from 11 to 1308
-- Stats: 19.8% null 3.83% unique
ALP integer,
-- Total protein. Normal range: 6.0 < N < 8.5. Values range from 0.0 to 9.9
-- Stats: 20.1% null 0.446% unique
TP real,
-- Albumin. Normal range: 3.5 < N < 5.5. Values range from 1.0 to 5.8
-- Stats: 20.4% null 0.28% unique
ALB real,
-- Uric acid. Normal range: N > 8.0 (Male), N > 6.5 (Female). Values range from 0.4 to 17.3
-- Stats: 20.2% null 0.949% unique
UA real,
-- Urea nitrogen. Normal range: N < 30. Values range from 0 to 152
-- Stats: 19.2% null 0.777% unique
UN integer,
-- Creatinine. Normal range: N < 1.5. Values range from 0.1 to 17.1
-- Stats: 19.1% null 0.467% unique
CRE real,
-- Stats: 30.8% null 0.288% unique
"T-BIL" real,
-- Stats: 23.3% null 2.34% unique
"T-CHO" integer,
-- Triglyceride. Normal range: N < 200. Values range from 1 to 867
-- Stats: 53.7% null 2.82% unique
TG integer,
-- Creatinine phosphokinase. Normal range: N < 250. Values range from 0 to 10835
-- Stats: 63.9% null 3.33% unique
CPK integer,
-- Blood glucose. Normal range: N < 180. Values range from 62 to 499
-- Stats: 87.7% null 1.5% unique
GLU integer,
-- White blood cell count. Normal range: 3.5 < N < 9.0. Values range from 0.9 to 35.2
-- Stats: 13.1% null 1.56% unique
WBC real,
-- Red blood cell count. Normal range: 3.5 < N < 6.0. Values range from 0.4 to 6.6
-- Stats: 13.1% null 0.403% unique
RBC real,
-- Hemoglobin. Normal range: 10 < N < 17. Values range from 1.3 to 18.9
-- Stats: 13.1% null 0.992% unique
HGB real,
-- Hematocrit. Normal range: 29 < N < 52. Values range from 3.0 to 56.0
-- Stats: 13.1% null 2.61% unique
HCT real,
-- Platelet count. Normal range: 100 < N < 400. Values range from 5 to 5844
-- Stats: 18.8% null 4.72% unique
PLT integer,
-- Prothrombin time. Normal range: N < 14. Values range from 10.1 to 27.0
-- Stats: 95.5% null 0.748% unique
PT real,
-- Activated partial prothrombin time. Normal range: N < 45. Values range from 57 to 146
-- Stats: 99.6% null 0.194% unique
APTT integer,
-- Fibrinogen. Normal range: 150 < N < 450. Values range from 23.8 to 106.5
-- Stats: 96.7% null 2.01% unique
FG real,
-- Values range from 114 to 700
-- Stats: 99.5% null 0.453% unique
PIC integer,
-- Values range from 63 to 183
-- Stats: 99% null 0.59% unique
TAT integer,
-- See TAT
-- Stats: 99.1% null 0.431% unique
TAT2 integer,
-- Stats: 30.5% null 0.115% unique
"U-PRO" text,
-- Immunoglobulin G. Normal range: 900 < N < 2000. Values range from 3 to 6510
-- Stats: 80.7% null 10.9% unique
IGG integer,
-- Immunoglobulin A. Normal range: 80 < N < 500. Values range from 1 to 1765
-- Stats: 80.7% null 4.9% unique
IGA integer,
-- Immunoglobulin M. Normal range: 40 < N < 400. Values range from 0 to 1573
-- Stats: 80.7% null 3.5% unique
IGM integer,
-- C-reactive protein. Normal range: N = -, +-, or N < 1.0. Values include '-', '<0.3', '<0.2', '+', '2+', '<0.002', '0.4', '0.3', '<0.1', '3+'
-- Stats: 17.6% null 1.52% unique
CRP text,
-- Rheumatoid Factor. Normal range: N = -, +-. Values include '-', '+', '2+', '+-', '7-'
-- Stats: 79.5% null 0.036% unique
RA text,
-- RAHA. Normal range: N < 20. Values include '<40', '<20.5', '<19.5', '<20.0', '<10', '<21.3', '<19.3', '40', '160', '<20.8'
-- Stats: 76% null 6.49% unique
RF text,
-- Complement 3. Normal range: N > 35. Values range from 15 to 196
-- Stats: 60.7% null 1.09% unique
C3 integer,
-- Complement 4. Normal range: N > 10. Values range from 3 to 80
-- Stats: 60.7% null 0.446% unique
C4 integer,
-- Anti-ribonuclear protein. Normal range: N = -, +-. Values include '0', 'negative', '4', '16', '1', '64', '256', '15'
-- Stats: 99% null 0.0575% unique
RNP text,
-- Anti-SM. Normal range: N = -, +-. Values include '0', 'negative', '1', '8', '2'
-- Stats: 99.1% null 0.036% unique
SM text,
-- Anti-scl70. Normal range: N = -, +-. Values include 'negative', '0', '4', '16', '1'
-- Stats: 99.8% null 0.036% unique
SC170 text,
-- Anti-SSA. Normal range: N = -, +-. Values include '0', 'negative', '16', '64', '4', '1', '256'
-- Stats: 99.3% null 0.0503% unique
SSA text,
-- Anti-SSB. Normal range: N = -, +-. Values include '0', 'negative', '32', '8', '2', '1'
-- Stats: 99.3% null 0.0431% unique
SSB text,
-- Anti-centromere. Normal range: N = -, +-. Values include '0', 'negative'
-- Stats: 99.9% null 0.0144% unique
CENTROMEA text,
-- Anti-DNA. Normal range: N < 8. Values range from 0.56 to 95.5
-- Stats: 99.5% null 0.475% unique
DNA text,
-- Stats: 100% null 0% unique
"DNA-II" integer
);