-- A comprehensive list of Formula 1 racing circuits, including their locations, coordinates, and reference information
-- 72 rows, primary key: (circuitId)
CREATE TABLE circuits (
-- Unique identification number of the circuit, ranging from 2 to 73
-- Stats: 0% null 100% unique
-- Foreign keys: races.circuitId (one-to-many)
circuitId integer,
-- Circuit reference name, e.g. 'zolder', 'zeltweg', 'zandvoort'
-- Stats: 0% null 100% unique
circuitRef text,
-- Full name of circuit
-- Stats: 0% null 100% unique
name text,
-- Location of circuit
-- Stats: 0% null 95.8% unique
location text,
-- Country of circuit
-- Stats: 0% null 44.4% unique
country text,
-- Latitude of location of circuit, ranging from -34.9272 to 57.2653
-- Stats: 0% null 98.6% unique
lat real,
-- Longitude of location of circuit. Location coordinates: (lat, lng)
-- Stats: 0% null 98.6% unique
lng real,
-- Not useful
-- Stats: 100% null 0% unique
alt integer,
-- Wikipedia URL for the circuit
-- Stats: 0% null 100% unique
url text
);
-- Comprehensive information about Formula 1 constructors, including their identifiers, names, nationalities, and reference links
-- 208 rows, primary key: (constructorId)
CREATE TABLE constructors (
-- Unique identification number for constructors, ranging from 1 to 210
-- Stats: 0% null 100% unique
-- Foreign keys: constructorResults.constructorId (one-to-many), constructorStandings.constructorId (one-to-many), qualifying.constructorId (one-to-many), results.constructorId (one-to-many)
constructorId integer,
-- Constructor reference name, alphabetically ordered from 'adams' to 'zakspeed'
-- Stats: 0% null 100% unique
constructorRef text,
-- Full name of the constructor
-- Stats: 0% null 100% unique
name text,
-- Nationality of the constructor, with 24 unique values including 'British', 'American', 'Italian', etc.
-- Stats: 0% null 11.5% unique
nationality text,
-- Wikipedia URL for detailed introduction of the constructor, e.g. 'http://en.wikipedia.org/wiki/Team_Lotus'
-- Stats: 0% null 82.2% unique
url text
);
-- Comprehensive information about Formula 1 drivers, including personal details and racing identifiers
-- 840 rows, primary key: (driverId)
CREATE TABLE drivers (
-- Unique identification number for each driver, ranging from 1 to 841
-- Stats: 0% null 100% unique
-- Foreign keys: driverStandings.driverId (one-to-many), lapTimes.driverId (one-to-many), pitStops.driverId (one-to-many), qualifying.driverId (one-to-many), results.driverId (one-to-many)
driverId integer,
-- Driver reference name, alphabetically ordered from 'Cannoc' to 'zunino'
-- Stats: 0% null 100% unique
driverRef text,
-- Driver's racing number, ranging from 2 to 99
-- Stats: 95.7% null 4.29% unique
"number" integer,
-- Abbreviated code for drivers. If "null" or empty, it means it doesn't have code. Examples: 'VER', 'MAG', 'BIA'
-- Stats: 90.1% null 9.52% unique
code text,
-- Driver's first name
-- Stats: 0% null 55.4% unique
forename text,
-- Driver's last name
-- Stats: 0% null 93.3% unique
surname text,
-- Driver's date of birth in YYYY-MM-DD format, ranging from 1896-12-28 to 1998-10-29
-- Stats: 0.119% null 97.7% unique
dob date,
-- Driver's nationality. Examples: 'British', 'American', 'Italian'
-- Stats: 0% null 4.88% unique
nationality text,
-- Introduction website of the driver, typically a Wikipedia link. Can be empty
-- Stats: 0% null 100% unique
url text
);
-- Formula One seasons information, including year and Wikipedia URL for each season
-- 68 rows, primary key: (year)
CREATE TABLE seasons (
-- Unique identification number for the Formula One season, ranging from 1950 to 2017
-- Stats: 0% null 100% unique
-- Foreign keys: races.year (one-to-many)
year integer,
-- Wikipedia link for the corresponding Formula One season, following the pattern 'http(s)://en.wikipedia.org/wiki/YYYY_Formula_One_season'
-- Stats: 0% null 100% unique
url text
);
-- Comprehensive record of Formula 1 races, including details such as date, time, location, and season information
-- 954 rows, primary key: (raceId)
CREATE TABLE races (
-- Unique identification number for each race, ranging from 2 to 988
-- Stats: 0% null 100% unique
-- Foreign keys: constructorResults.raceId (one-to-many), constructorStandings.raceId (one-to-many), driverStandings.raceId (one-to-many), lapTimes.raceId (one-to-many), pitStops.raceId (one-to-many), qualifying.raceId (one-to-many), results.raceId (one-to-many)
raceId integer,
-- Year of the race, ranging from 1950 to 2017
-- Stats: 0% null 7.13% unique
-- Foreign keys: seasons.year (many-to-one)
year integer,
-- Round number of the race in the season, ranging from 1 to 21
-- Stats: 0% null 2.2% unique
round integer,
-- Unique identifier for the circuit, ranging from 2 to 73
-- Stats: 0% null 7.44% unique
-- Foreign keys: circuits.circuitId (many-to-one)
circuitId integer,
-- Name of the Grand Prix race, e.g., 'Italian Grand Prix', 'British Grand Prix'
-- Stats: 0% null 4.4% unique
name text,
-- Date of the race in YYYY-MM-DD format, ranging from 1950-05-13 to 2017-11-26
-- Stats: 0% null 100% unique
"date" date,
-- Start time of the race in HH:MM:SS format, ranging from 04:30:00 to 20:00:00
-- Stats: 75.7% null 1.99% unique
"time" text,
-- Wikipedia URL with information about the race
-- Stats: 0% null 100% unique
url text
);
-- Contains constructor results for races, including identifiers, points scored, and status.
-- 11082 rows, primary key: (constructorResultsId)
CREATE TABLE constructorResults (
-- Unique identifier for constructor results. Integer values ranging from 1 to 15579.
-- Stats: 0% null 100% unique
constructorResultsId integer,
-- Identifier for the race. Integer values ranging from 1 to 982.
-- Stats: 0% null 8.18% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Identifier for the constructor. Integer values ranging from 1 to 210.
-- Stats: 0% null 1.55% unique
-- Foreign keys: constructors.constructorId (many-to-one)
constructorId integer,
-- Points scored. Decimal values ranging from 0.0 to 66.0.
-- Stats: 0% null 0.406% unique
points real,
-- Status of the constructor result. All values are 'D'.
-- Stats: 99.8% null 0.00902% unique
status text
);
-- Records of constructor standings in Formula 1 races, including race and constructor identifiers, points earned, positions, and wins
-- 11836 rows, primary key: (constructorStandingsId)
CREATE TABLE constructorStandings (
-- Unique identifier for constructor standing records, ranging from 1 to 26872
-- Stats: 0% null 100% unique
constructorStandingsId integer,
-- Identifier for races, ranging from 1 to 982
-- Stats: 0% null 7.65% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Identifier for constructors, ranging from 1 to 210
-- Stats: 0% null 1.32% unique
-- Foreign keys: constructors.constructorId (many-to-one)
constructorId integer,
-- Points acquired in each race, ranging from 0.0 to 765.0
-- Stats: 0% null 3.68% unique
points real,
-- Position in the race, ranging from 1 to 22
-- Stats: 0% null 0.186% unique
position integer,
-- Same as position, not quite useful. Values include '1', '2', '3', ..., 'E'
-- Stats: 0% null 0.194% unique
positionText text,
-- Number of wins, ranging from 0 to 19
-- Stats: 0% null 0.169% unique
wins integer
);
-- Records of driver standings in races, including race and driver identifiers, points earned, positions, and wins
-- 31578 rows, primary key: (driverStandingsId)
CREATE TABLE driverStandings (
-- Unique identifier for driver standing records, ranging from 1 to 68460
-- Stats: 0% null 100% unique
driverStandingsId integer,
-- Identifier for races, ranging from 1 to 982
-- Stats: 0% null 3.07% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Identifier for drivers, ranging from 1 to 841
-- Stats: 0% null 2.64% unique
-- Foreign keys: drivers.driverId (many-to-one)
driverId integer,
-- Points acquired in each race, ranging from 0.0 to 397.0
-- Stats: 0% null 1.07% unique
points real,
-- Position in the race, ranging from 1 to 108
-- Stats: 0% null 0.342% unique
position integer,
-- Same as position, not quite useful. Values include '1', '2', '3', ..., up to 'D'
-- Stats: 0% null 0.345% unique
positionText text,
-- Number of wins, ranging from 0 to 13
-- Stats: 0% null 0.0443% unique
wins integer
);
-- Contains detailed lap time information for Formula 1 races, including race and driver identifiers, lap numbers, positions, and timing data.
-- 400524 rows, primary key: (raceId, driverId, lap)
CREATE TABLE lapTimes (
-- Unique identifier for each race. Integer values ranging from 2 to 982.
-- Stats: 0% null 0.0916% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Unique identifier for each driver. Integer values ranging from 1 to 841.
-- Stats: 0% null 0.0302% unique
-- Foreign keys: drivers.driverId (many-to-one)
driverId integer,
-- Lap number in the race. Integer values from 1 to 78.
-- Stats: 0% null 0.0195% unique
lap integer,
-- Driver's position on the track. Integer values from 1 to 24.
-- Stats: 0% null 0.00599% unique
position integer,
-- Lap time in the format 'minutes:seconds.milliseconds'. Examples: '1:23.794', '1:21.571'.
-- Stats: 0% null 16.7% unique
"time" text,
-- See time. Integer representation of lap time in milliseconds.
-- Stats: 0% null 16.7% unique
milliseconds integer
);
-- Records of pit stops during races, including timing and duration information
-- 5815 rows, primary key: (raceId, driverId, stop)
CREATE TABLE pitStops (
-- Unique identifier for each race, ranging from 842 to 982
-- Stats: 0% null 2.13% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Unique identifier for each driver, ranging from 1 to 841
-- Stats: 0% null 0.929% unique
-- Foreign keys: drivers.driverId (many-to-one)
driverId integer,
-- Pit stop number, ranging from 1 to 6
-- Stats: 0% null 0.103% unique
stop integer,
-- Lap number when the pit stop occurred, ranging from 1 to 74
-- Stats: 0% null 1.26% unique
lap integer,
-- Exact time of the pit stop in 'HH:MM:SS' format
-- Stats: 0% null 80% unique
"time" text,
-- Duration of the pit stop in seconds, with decimal precision
-- Stats: 0% null 78.8% unique
duration text,
-- See duration
-- Stats: 0% null 78.8% unique
milliseconds integer
);
-- Detailed qualifying results for Formula 1 races, including times for each qualifying session and final positions.
-- 6967 rows, primary key: (qualifyId)
CREATE TABLE qualifying (
-- Unique identifier for qualifying sessions. Values range from 23 to 7419.
-- Stats: 0% null 100% unique
qualifyId integer,
-- Identifier for each race. Values range from 2 to 982.
-- Stats: 0% null 4.58% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Identifier for each driver. Values range from 1 to 841.
-- Stats: 0% null 2.17% unique
-- Foreign keys: drivers.driverId (many-to-one)
driverId integer,
-- Identifier for each constructor. Values range from 1 to 210.
-- Stats: 0% null 0.588% unique
-- Foreign keys: constructors.constructorId (many-to-one)
constructorId integer,
-- Driver's car number. Values range from 0 to 99.
-- Stats: 0% null 0.689% unique
"number" integer,
-- Qualifying position. Values range from 1 to 28.
-- Stats: 0% null 0.402% unique
position integer,
-- Time in Q1 session, format: 'minutes:seconds.milliseconds'. All drivers participate. Determines positions 1-15 for Q2. Sample: '1:20.888'
-- Stats: 1.56% null 90.2% unique
q1 text,
-- See q1. Only top 15 from Q1 participate. Determines positions 1-10 for Q3. Empty string if driver didn't participate.
-- Stats: 51.3% null 46.2% unique
q2 text,
-- See q1. Only top 10 from Q2 participate. Determines final grid positions 1-10. Empty string if driver didn't participate.
-- Stats: 70.8% null 28.1% unique
q3 text
);
-- Contains various status descriptions with their corresponding unique identifiers
-- 134 rows, primary key: (statusId)
CREATE TABLE status (
-- Unique identification number for status, ranging from 1 to 136
-- Stats: 0% null 100% unique
-- Foreign keys: results.statusId (one-to-many)
statusId integer,
-- Full name of status. Examples include 'Withdrew', 'Wheel rim', 'Wheel nut', 'Wheel bearing', 'Wheel', etc.
-- Stats: 0% null 100% unique
status text
);
-- Comprehensive race results table containing detailed information about each driver's performance in Formula 1 races
-- 23179 rows, primary key: (resultId)
CREATE TABLE results (
-- Unique identification number for race result
-- Stats: 0% null 100% unique
resultId integer,
-- Identification number for the race
-- Stats: 0% null 4.09% unique
-- Foreign keys: races.raceId (many-to-one)
raceId integer,
-- Identification number for the driver
-- Stats: 0% null 3.62% unique
-- Foreign keys: drivers.driverId (many-to-one)
driverId integer,
-- Identification number for the constructor
-- Stats: 0% null 0.893% unique
-- Foreign keys: constructors.constructorId (many-to-one)
constructorId integer,
-- Driver's car number
-- Stats: 0.0259% null 0.552% unique
"number" integer,
-- Starting position on the grid. Range: 0-34
-- Stats: 0% null 0.151% unique
grid integer,
-- Finishing position. Range: 1-33
-- Stats: 44.5% null 0.142% unique
position integer,
-- Finishing position as text. Not quite useful. Values include 'R', 'F', and numbers
-- Stats: 0% null 0.168% unique
positionText text,
-- See position
-- Stats: 0% null 0.168% unique
positionOrder integer,
-- Points scored in the race. Range: 0.0-50.0
-- Stats: 0% null 0.142% unique
points real,
-- Number of laps completed. Range: 0-200
-- Stats: 0% null 0.742% unique
laps integer,
-- Finish time. Champion's time in 'minutes:seconds.milliseconds', others as '+seconds.milliseconds' relative to champion
-- Stats: 75% null 24.1% unique
"time" text,
-- Actual finishing time in milliseconds
-- Stats: 75% null 24.8% unique
milliseconds integer,
-- Lap number of the driver's fastest lap. Range: 2-78
-- Stats: 78.5% null 0.332% unique
fastestLap integer,
-- Starting rank based on fastest lap speed. Range: 0-24
-- Stats: 77.9% null 0.108% unique
rank integer,
-- Fastest lap time. Format: 'minutes:seconds.milliseconds'. Smaller value leads to higher rank
-- Stats: 78.5% null 20.3% unique
fastestLapTime text,
-- Fastest lap speed in km/h
-- Stats: 78.5% null 20.7% unique
fastestLapSpeed text,
-- Status ID. Corresponding descriptions appear in the 'status' table
-- Stats: 0% null 0.565% unique
-- Foreign keys: status.statusId (many-to-one)
statusId integer
);