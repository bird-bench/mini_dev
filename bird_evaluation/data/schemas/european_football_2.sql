-- Comprehensive table of player attributes in soccer, including various skills, physical attributes, and goalkeeper-specific ratings.
-- 183978 rows, primary key: (id)
CREATE TABLE Player_Attributes (
-- Unique identifier for players, ranging from 1 to 183978
-- Stats: 0% null 100% unique
id integer,
-- FIFA API player ID, ranging from 2 to 234141
-- Stats: 0% null 6.01% unique
-- Foreign keys: Player.player_fifa_api_id (many-to-one)
player_fifa_api_id integer,
-- API player ID, ranging from 2625 to 750584
-- Stats: 0% null 6.01% unique
-- Foreign keys: Player.player_api_id (many-to-one)
player_api_id integer,
-- Date in format 'YYYY-MM-DD HH:MM:SS', ranging from '2007-02-22 00:00:00' to '2016-07-07 00:00:00'
-- Stats: 0% null 0.107% unique
"date" text,
-- Player's overall strength rating (0-100). Higher is stronger.
-- Stats: 0.454% null 0.0332% unique
overall_rating integer,
-- Player's potential score (0-100). Higher indicates more potential.
-- Stats: 0.454% null 0.0304% unique
potential integer,
-- Player's preferred foot for attacking: 'right' or 'left'
-- Stats: 0.454% null 0.00109% unique
preferred_foot text,
-- Player's attacking work rate: 'high', 'medium', 'low'. Some inconsistent values present.
-- Stats: 1.76% null 0.00435% unique
attacking_work_rate text,
-- Player's defensive work rate: 'high', 'medium', 'low'. Some inconsistent values present.
-- Stats: 0.454% null 0.0103% unique
defensive_work_rate text,
-- Player's crossing score (0-100). Higher is better.
-- Stats: 0.454% null 0.0516% unique
crossing integer,
-- See crossing
-- Stats: 0.454% null 0.0527% unique
finishing integer,
-- See crossing
-- Stats: 0.454% null 0.0522% unique
heading_accuracy integer,
-- See crossing
-- Stats: 0.454% null 0.0516% unique
short_passing integer,
-- See crossing
-- Stats: 1.47% null 0.0505% unique
volleys integer,
-- See crossing
-- Stats: 0.454% null 0.0527% unique
dribbling integer,
-- See crossing
-- Stats: 1.47% null 0.05% unique
curve integer,
-- See crossing
-- Stats: 0.454% null 0.0527% unique
free_kick_accuracy integer,
-- See crossing
-- Stats: 0.454% null 0.0516% unique
long_passing integer,
-- See crossing
-- Stats: 0.454% null 0.0505% unique
ball_control integer,
-- See crossing
-- Stats: 0.454% null 0.0467% unique
acceleration integer,
-- See crossing
-- Stats: 0.454% null 0.0462% unique
sprint_speed integer,
-- See crossing
-- Stats: 1.47% null 0.044% unique
agility integer,
-- See crossing
-- Stats: 0.454% null 0.0424% unique
reactions integer,
-- See crossing
-- Stats: 1.47% null 0.044% unique
balance integer,
-- See crossing
-- Stats: 0.454% null 0.0522% unique
shot_power integer,
-- See crossing
-- Stats: 1.47% null 0.0429% unique
jumping integer,
-- See crossing
-- Stats: 0.454% null 0.0457% unique
stamina integer,
-- See crossing
-- Stats: 0.454% null 0.0446% unique
strength integer,
-- See crossing
-- Stats: 0.454% null 0.0522% unique
long_shots integer,
-- See crossing
-- Stats: 0.454% null 0.0495% unique
aggression integer,
-- See crossing
-- Stats: 0.454% null 0.0522% unique
interceptions integer,
-- See crossing
-- Stats: 0.454% null 0.0516% unique
positioning integer,
-- See crossing
-- Stats: 1.47% null 0.0527% unique
vision integer,
-- See crossing
-- Stats: 0.454% null 0.0511% unique
penalties integer,
-- See crossing
-- Stats: 0.454% null 0.0516% unique
marking integer,
-- See crossing
-- Stats: 0.454% null 0.0516% unique
standing_tackle integer,
-- See crossing
-- Stats: 1.47% null 0.0511% unique
sliding_tackle integer,
-- Goalkeeper diving score (0-100). Higher is better.
-- Stats: 0.454% null 0.0505% unique
gk_diving integer,
-- Goalkeeper handling score (0-100). Higher is better.
-- Stats: 0.454% null 0.0489% unique
gk_handling integer,
-- Goalkeeper kicking score (0-100). Higher is better.
-- Stats: 0.454% null 0.0527% unique
gk_kicking integer,
-- Goalkeeper positioning score (0-100). Higher is better.
-- Stats: 0.454% null 0.0511% unique
gk_positioning integer,
-- Goalkeeper reflexes score (0-100). Higher is better.
-- Stats: 0.454% null 0.05% unique
gk_reflexes integer
);
-- Comprehensive player information table including personal details and various identification numbers for football/soccer players
-- 11060 rows, primary key: (id)
CREATE TABLE Player (
-- Unique identifier for players, ranging from 1 to 11075
-- Stats: 0% null 100% unique
id integer,
-- Player API identifier, ranging from 2625 to 750584
-- Stats: 0% null 100% unique
-- Foreign keys: Player_Attributes.player_api_id (one-to-many), Match.away_player_11 (one-to-many), Match.away_player_10 (one-to-many), Match.away_player_9 (one-to-many), Match.away_player_8 (one-to-many), Match.away_player_7 (one-to-many), Match.away_player_6 (one-to-many), Match.away_player_5 (one-to-many), Match.away_player_4 (one-to-many), Match.away_player_3 (one-to-many), Match.away_player_2 (one-to-many), Match.away_player_1 (one-to-many), Match.home_player_11 (one-to-many), Match.home_player_10 (one-to-many), Match.home_player_9 (one-to-many), Match.home_player_8 (one-to-many), Match.home_player_7 (one-to-many), Match.home_player_6 (one-to-many), Match.home_player_5 (one-to-many), Match.home_player_4 (one-to-many), Match.home_player_3 (one-to-many), Match.home_player_2 (one-to-many), Match.home_player_1 (one-to-many)
player_api_id integer,
-- Full name of the player
-- Stats: 0% null 98.1% unique
player_name text,
-- FIFA API identifier for the player, ranging from 2 to 234141
-- Stats: 0% null 100% unique
-- Foreign keys: Player_Attributes.player_fifa_api_id (one-to-many)
player_fifa_api_id integer,
-- Player's date of birth in 'YYYY-MM-DD HH:MM:SS' format, ranging from '1967-01-23 00:00:00' to '1999-04-24 00:00:00'. Earlier date indicates older player.
-- Stats: 0% null 52.1% unique
birthday text,
-- Player's height in centimeters, ranging from 157 to 208
-- Stats: 0% null 0.181% unique
height integer,
-- Player's weight, likely in pounds, ranging from 117 to 243
-- Stats: 0% null 0.452% unique
weight integer
);
-- Contains information about soccer leagues, including their unique identifiers, associated country IDs, and full names.
-- 11 rows, primary key: (id)
CREATE TABLE League (
-- Unique identifier for leagues. Integer values ranging from 1 to 24558.
-- Stats: 0% null 100% unique
id integer,
-- See id. Represents the unique identifier for countries.
-- Stats: 0% null 100% unique
-- Foreign keys: Country.id (one-to-one)
country_id integer,
-- Full name of the soccer league. Examples include 'England Premier League', 'Spain LIGA BBVA', 'Germany 1. Bundesliga'.
-- Stats: 0% null 100% unique
name text
);
-- A table containing basic information about countries, primarily focused on European nations
-- 11 rows, primary key: (id)
CREATE TABLE Country (
-- Unique identifier for each country, ranging from 1 to 24558
-- Stats: 0% null 100% unique
-- Foreign keys: League.country_id (one-to-one)
id integer,
-- Full name of the country
-- Stats: 0% null 100% unique
name text
);
-- Contains information about soccer teams, including various identifiers and team names
-- 299 rows, primary key: (id)
CREATE TABLE Team (
-- Unique identifier for teams, ranging from 1 to 51606
-- Stats: 0% null 100% unique
id integer,
-- Team API identifier, ranging from 1601 to 274581
-- Stats: 0% null 100% unique
-- Foreign keys: Team_Attributes.team_api_id (one-to-many), Match.away_team_api_id (one-to-many), Match.home_team_api_id (one-to-many)
team_api_id integer,
-- FIFA API identifier for teams, ranging from 1 to 112513
-- Stats: 3.68% null 95.3% unique
-- Foreign keys: Team_Attributes.team_fifa_api_id (many-to-many)
team_fifa_api_id integer,
-- Full name of the team, e.g. 'Widzew Łódź', 'Royal Excel Mouscron'
-- Stats: 0% null 99% unique
team_long_name text,
-- Abbreviated team name, typically 3 letters, e.g. 'VAL', 'POR', 'MON'
-- Stats: 0% null 86.6% unique
team_short_name text
);
-- Comprehensive table of team attributes covering various aspects of gameplay, including build-up play, chance creation, and defensive strategies
-- 1458 rows, primary key: (id)
CREATE TABLE Team_Attributes (
-- Unique identifier for teams, ranging from 1 to 1458
-- Stats: 0% null 100% unique
id integer,
-- FIFA API team identifier, ranging from 1 to 112513
-- Stats: 0% null 19.5% unique
-- Foreign keys: Team.team_fifa_api_id (many-to-many)
team_fifa_api_id integer,
-- API team identifier, ranging from 1601 to 274581
-- Stats: 0% null 19.8% unique
-- Foreign keys: Team.team_api_id (many-to-one)
team_api_id integer,
-- Date of record, format: 'YYYY-MM-DD HH:MM:SS', range: '2010-02-22 00:00:00' to '2015-09-10 00:00:00'
-- Stats: 0% null 0.412% unique
"date" text,
-- Speed of attack build-up, score between 20-80
-- Stats: 0% null 3.91% unique
buildUpPlaySpeed integer,
-- Attack speed classification: 'Slow' (1-33), 'Balanced' (34-66), or 'Fast' (66-100)
-- Stats: 0% null 0.206% unique
buildUpPlaySpeedClass text,
-- Dribbling tendency/frequency, score between 24-77
-- Stats: 66.5% null 3.36% unique
buildUpPlayDribbling integer,
-- Dribbling classification: 'Little' (1-33), 'Normal' (34-66), or 'Lots' (66-100)
-- Stats: 0% null 0.206% unique
buildUpPlayDribblingClass text,
-- Affects passing distance and teammate support, score between 20-80
-- Stats: 0% null 3.98% unique
buildUpPlayPassing integer,
-- Passing classification: 'Short' (1-33), 'Mixed' (34-66), or 'Long' (66-100)
-- Stats: 0% null 0.206% unique
buildUpPlayPassingClass text,
-- Team's movement freedom in first 2/3 of pitch: 'Organised' or 'Free Form'
-- Stats: 0% null 0.137% unique
buildUpPlayPositioningClass text,
-- Risk in pass decisions and run support, score between 21-80
-- Stats: 0% null 3.43% unique
chanceCreationPassing integer,
-- Chance creation passing classification: 'Safe' (1-33), 'Normal' (34-66), or 'Risky' (66-100)
-- Stats: 0% null 0.206% unique
chanceCreationPassingClass text,
-- Tendency/frequency of crosses into the box, score between 20-80
-- Stats: 0% null 3.84% unique
chanceCreationCrossing integer,
-- Chance creation crossing classification: 'Little' (1-33), 'Normal' (34-66), or 'Lots' (66-100)
-- Stats: 0% null 0.206% unique
chanceCreationCrossingClass text,
-- Tendency/frequency of shots taken, score between 22-80
-- Stats: 0% null 3.91% unique
chanceCreationShooting integer,
-- Chance creation shooting classification: 'Little' (1-33), 'Normal' (34-66), or 'Lots' (66-100)
-- Stats: 0% null 0.206% unique
chanceCreationShootingClass text,
-- Team's movement freedom in final third of pitch: 'Organised' or 'Free Form'
-- Stats: 0% null 0.137% unique
chanceCreationPositioningClass text,
-- Affects how high up the pitch the team starts pressuring, score between 23-72
-- Stats: 0% null 3.29% unique
defencePressure integer,
-- Defence pressure classification: 'Deep' (1-33), 'Medium' (34-66), or 'High' (66-100)
-- Stats: 0% null 0.206% unique
defencePressureClass text,
-- Team's approach to tackling ball possessor, score between 24-72
-- Stats: 0% null 3.22% unique
defenceAggression integer,
-- Defence aggression classification: 'Contain' (1-33), 'Press' (34-66), or 'Double' (66-100)
-- Stats: 0% null 0.206% unique
defenceAggressionClass text,
-- Affects team's shift to ball side, score between 29-73
-- Stats: 0% null 2.95% unique
defenceTeamWidth integer,
-- Defence team width classification: 'Narrow' (1-33), 'Normal' (34-66), or 'Wide' (66-100)
-- Stats: 0% null 0.206% unique
defenceTeamWidthClass text,
-- Defence shape and strategy: 'Cover' or 'Offside Trap'
-- Stats: 0% null 0.137% unique
defenceDefenderLineClass text
);
-- A comprehensive soccer match database containing detailed information about matches, players, events, and betting odds from various bookmakers
-- 25979 rows, primary key: (id)
CREATE TABLE Match (
-- Unique identifier for matches, ranging from 1 to 25979
-- Stats: 0% null 100% unique
id integer,
-- Country identifier, ranging from 1 to 24558
-- Stats: 0% null 0.0423% unique
country_id integer,
-- League identifier, ranging from 1 to 24558
-- Stats: 0% null 0.0423% unique
league_id integer,
-- Season of the match, e.g. '2015/2016'
-- Stats: 0% null 0.0308% unique
season text,
-- Stage of the match, ranging from 1 to 38
-- Stats: 0% null 0.146% unique
stage integer,
-- Date of the match, e.g. '2008-08-17 00:00:00'
-- Stats: 0% null 6.52% unique
"date" text,
-- Match API identifier, ranging from 483129 to 2216672
-- Stats: 0% null 100% unique
match_api_id integer,
-- Home team API identifier, ranging from 1601 to 274581
-- Stats: 0% null 1.15% unique
-- Foreign keys: Team.team_api_id (many-to-one)
home_team_api_id integer,
-- Away team API identifier, ranging from 1601 to 274581
-- Stats: 0% null 1.15% unique
-- Foreign keys: Team.team_api_id (many-to-one)
away_team_api_id integer,
-- Number of goals scored by home team, ranging from 0 to 10
-- Stats: 0% null 0.0423% unique
home_team_goal integer,
-- Number of goals scored by away team, ranging from 0 to 9
-- Stats: 0% null 0.0385% unique
away_team_goal integer,
-- See home_player_X2
-- Stats: 7.01% null 0.0115% unique
home_player_X1 integer,
-- Player position on the field for home team, ranging from 0 to 9
-- Stats: 7.01% null 0.0346% unique
home_player_X2 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0308% unique
home_player_X3 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0269% unique
home_player_X4 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
home_player_X5 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
home_player_X6 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
home_player_X7 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
home_player_X8 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
home_player_X9 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
home_player_X10 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0231% unique
home_player_X11 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0115% unique
away_player_X1 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0308% unique
away_player_X2 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0308% unique
away_player_X3 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0308% unique
away_player_X4 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
away_player_X5 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
away_player_X6 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
away_player_X7 integer,
-- See home_player_X2
-- Stats: 7.05% null 0.0346% unique
away_player_X8 integer,
-- See home_player_X2
-- Stats: 7.06% null 0.0346% unique
away_player_X9 integer,
-- See home_player_X2
-- Stats: 7.06% null 0.0346% unique
away_player_X10 integer,
-- See home_player_X2
-- Stats: 7.08% null 0.0231% unique
away_player_X11 integer,
-- Player position on the field for home team, ranging from 0 to 11
-- Stats: 7.01% null 0.0115% unique
home_player_Y1 integer,
-- See home_player_Y1
-- Stats: 7.01% null 0.0077% unique
home_player_Y2 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0077% unique
home_player_Y3 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0077% unique
home_player_Y4 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0192% unique
home_player_Y5 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0231% unique
home_player_Y6 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0231% unique
home_player_Y7 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0269% unique
home_player_Y8 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0231% unique
home_player_Y9 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0269% unique
home_player_Y10 integer,
-- See home_player_Y1
-- Stats: 7.05% null 0.0154% unique
home_player_Y11 integer,
-- Player position on the field for away team, ranging from 1 to 11
-- Stats: 7.05% null 0.0077% unique
away_player_Y1 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.00385% unique
away_player_Y2 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.0077% unique
away_player_Y3 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.0115% unique
away_player_Y4 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.0192% unique
away_player_Y5 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.0269% unique
away_player_Y6 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.0269% unique
away_player_Y7 integer,
-- See away_player_Y1
-- Stats: 7.05% null 0.0269% unique
away_player_Y8 integer,
-- See away_player_Y1
-- Stats: 7.06% null 0.0269% unique
away_player_Y9 integer,
-- See away_player_Y1
-- Stats: 7.06% null 0.0231% unique
away_player_Y10 integer,
-- See away_player_Y1
-- Stats: 7.08% null 0.0154% unique
away_player_Y11 integer,
-- Player identifier for home team, ranging from 2984 to 698273
-- Stats: 4.71% null 3.49% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_1 integer,
-- See home_player_1
-- Stats: 5.06% null 9.29% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_2 integer,
-- See home_player_1
-- Stats: 4.93% null 9.14% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_3 integer,
-- See home_player_1
-- Stats: 5.09% null 10% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_4 integer,
-- See home_player_1
-- Stats: 5.07% null 10.7% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_5 integer,
-- See home_player_1
-- Stats: 5.1% null 14.6% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_6 integer,
-- See home_player_1
-- Stats: 4.72% null 13.2% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_7 integer,
-- See home_player_1
-- Stats: 5.04% null 15.7% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_8 integer,
-- See home_player_1
-- Stats: 4.9% null 15.8% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_9 integer,
-- See home_player_1
-- Stats: 5.53% null 14% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_10 integer,
-- See home_player_1
-- Stats: 5.99% null 11.1% unique
-- Foreign keys: Player.player_api_id (many-to-one)
home_player_11 integer,
-- Player identifier for away team, ranging from 2796 to 698273
-- Stats: 4.75% null 3.56% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_1 integer,
-- See away_player_1
-- Stats: 4.92% null 9.64% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_2 integer,
-- See away_player_1
-- Stats: 4.98% null 9.51% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_3 integer,
-- See away_player_1
-- Stats: 5.08% null 10.2% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_4 integer,
-- See away_player_1
-- Stats: 5.14% null 11.1% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_5 integer,
-- See away_player_1
-- Stats: 5.05% null 15.1% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_6 integer,
-- See away_player_1
-- Stats: 4.75% null 13.9% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_7 integer,
-- See away_player_1
-- Stats: 5.16% null 16.4% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_8 integer,
-- See away_player_1
-- Stats: 5.11% null 16.6% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_9 integer,
-- See away_player_1
-- Stats: 5.55% null 15% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_10 integer,
-- See away_player_1
-- Stats: 5.98% null 11.7% unique
-- Foreign keys: Player.player_api_id (many-to-one)
away_player_11 integer,
-- XML data containing goal information
-- Stats: 45.3% null 50.9% unique
goal text,
-- XML data containing shot on goal information
-- Stats: 45.3% null 32.6% unique
shoton text,
-- XML data containing shot off goal information
-- Stats: 45.3% null 32.6% unique
shotoff text,
-- XML data containing foul information
-- Stats: 45.3% null 32.6% unique
foulcommit text,
-- XML data containing card information
-- Stats: 45.3% null 53% unique
card text,
-- XML data containing cross information
-- Stats: 45.3% null 32.6% unique
"cross" text,
-- XML data containing corner kick information
-- Stats: 45.3% null 32.6% unique
corner text,
-- XML data containing possession information
-- Stats: 45.3% null 32.4% unique
possession text,
-- Bet365 odds for home team win, ranging from 1.04 to 26.0
-- Stats: 13% null 0.466% unique
B365H real,
-- Bet365 odds for draw, ranging from 1.4 to 17.0
-- Stats: 13% null 0.277% unique
B365D real,
-- Bet365 odds for away team win, ranging from 1.08 to 51.0
-- Stats: 13% null 0.443% unique
B365A real,
-- Bwin odds for home team win, ranging from 1.03 to 34.0
-- Stats: 13.1% null 0.912% unique
BWH real,
-- Bwin odds for draw, ranging from 1.65 to 19.5
-- Stats: 13.1% null 0.512% unique
BWD real,
-- Bwin odds for away team win, ranging from 1.1 to 51.0
-- Stats: 13.1% null 1% unique
BWA real,
-- Interwetten odds for home team win, ranging from 1.03 to 20.0
-- Stats: 13.3% null 0.566% unique
IWH real,
-- Interwetten odds for draw, ranging from 1.5 to 11.0
-- Stats: 13.3% null 0.281% unique
IWD real,
-- Interwetten odds for away team win, ranging from 1.1 to 25.0
-- Stats: 13.3% null 0.612% unique
IWA real,
-- Ladbrokes odds for home team win, ranging from 1.04 to 26.0
-- Stats: 13.2% null 0.497% unique
LBH real,
-- Ladbrokes odds for draw, ranging from 1.4 to 19.0
-- Stats: 13.2% null 0.277% unique
LBD real,
-- Ladbrokes odds for away team win, ranging from 1.1 to 51.0
-- Stats: 13.2% null 0.493% unique
LBA real,
-- Pinnacle odds for home team win, ranging from 1.04 to 36.0
-- Stats: 57% null 3.65% unique
PSH real,
-- Pinnacle odds for draw, ranging from 2.2 to 29.0
-- Stats: 57% null 2.56% unique
PSD real,
-- Pinnacle odds for away team win, ranging from 1.09 to 47.5
-- Stats: 57% null 5.68% unique
PSA real,
-- William Hill odds for home team win, ranging from 1.02 to 26.0
-- Stats: 13.1% null 0.481% unique
WHH real,
-- William Hill odds for draw, ranging from 1.02 to 17.0
-- Stats: 13.1% null 0.3% unique
WHD real,
-- William Hill odds for away team win, ranging from 1.08 to 51.0
-- Stats: 13.1% null 0.523% unique
WHA real,
-- Stan James odds for home team win, ranging from 1.04 to 23.0
-- Stats: 34.2% null 0.527% unique
SJH real,
-- Stan James odds for draw, ranging from 1.4 to 15.0
-- Stats: 34.2% null 0.304% unique
SJD real,
-- Stan James odds for away team win, ranging from 1.1 to 41.0
-- Stats: 34.2% null 0.508% unique
SJA real,
-- VC Bet odds for home team win, ranging from 1.03 to 36.0
-- Stats: 13.1% null 0.616% unique
VCH real,
-- VC Bet odds for draw, ranging from 1.62 to 26.0
-- Stats: 13.1% null 0.316% unique
VCD real,
-- VC Bet odds for away team win, ranging from 1.08 to 67.0
-- Stats: 13.1% null 0.581% unique
VCA real,
-- Gamebookers odds for home team win, ranging from 1.05 to 21.0
-- Stats: 45.5% null 0.612% unique
GBH real,
-- Gamebookers odds for draw, ranging from 1.45 to 11.0
-- Stats: 45.5% null 0.323% unique
GBD real,
-- Gamebookers odds for away team win, ranging from 1.12 to 34.0
-- Stats: 45.5% null 0.662% unique
GBA real,
-- Blue Square odds for home team win, ranging from 1.04 to 17.0
-- Stats: 45.5% null 0.389% unique
BSH real,
-- Blue Square odds for draw, ranging from 1.33 to 13.0
-- Stats: 45.5% null 0.227% unique
BSD real,
-- Blue Square odds for away team win, ranging from 1.12 to 34.0
-- Stats: 45.5% null 0.37% unique
BSA real
);