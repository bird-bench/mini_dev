-- Contains superhero alignment information, categorizing characters based on their moral and ethical stances
-- 4 rows, primary key: (id)
CREATE TABLE alignment (
-- alignment
-- Stats: 0% null 100% unique
-- Foreign keys: superhero.alignment_id (one-to-many)
id integer,
-- [
--   {
--     "name": "id",
--     "description": "Unique identifier of the alignment, ranging from 1 to 4"
--   },
--   {
--     "name": "alignment",
--     "description": "Moral and ethical stance of the superhero. Possible values include 'Good' (kind, selfless, protecting others), 'Neutral' (may act in self-interest or follow own moral code), 'Bad' (selfish, manipulative), and 'N/A'. Examples: Superman (Good), Hulk (Neutral), Lex Luthor (Bad)."
--   }
-- ]
-- Stats: 0% null 100% unique
alignment text
);
-- A table listing various superhero attributes with their unique identifiers
-- 6 rows, primary key: (id)
CREATE TABLE attribute (
-- Unique identifier for each attribute, ranging from 1 to 6
-- Stats: 0% null 100% unique
-- Foreign keys: hero_attribute.attribute_id (one-to-many)
id integer,
-- Superhero attribute. Commonsense evidence: A superhero's attribute is a characteristic or quality that defines who they are and what they are capable of. This could be a physical trait, such as superhuman strength or the ability to fly, or a personal trait, such as extraordinary intelligence or exceptional bravery. Sample values: 'Strength', 'Speed', 'Power', 'Intelligence', 'Durability', 'Combat'
-- Stats: 0% null 100% unique
attribute_name text
);
-- A table containing unique color identifiers and corresponding color descriptions for superhero features
-- 35 rows, primary key: (id)
CREATE TABLE colour (
-- The unique identifier of the color, ranging from 1 to 35
-- Stats: 0% null 100% unique
-- Foreign keys: superhero.skin_colour_id (one-to-many), superhero.hair_colour_id (one-to-many), superhero.eye_colour_id (one-to-many)
id integer,
-- The color of the superhero's skin/eye/hair/etc. Includes single colors (e.g. 'Yellow', 'White', 'Violet') and color combinations (e.g. 'Yellow/Red', 'Red/White')
-- Stats: 0% null 100% unique
colour text
);
-- A table containing gender information for superheroes, including a unique identifier and gender category
-- 3 rows, primary key: (id)
CREATE TABLE gender (
-- Unique identifier for gender, ranging from 1 to 3
-- Stats: 0% null 100% unique
-- Foreign keys: superhero.gender_id (one-to-many)
id integer,
-- Gender of the superhero. Values include 'N/A', 'Male', and 'Female'
-- Stats: 0% null 100% unique
gender text
);
-- A table containing information about publishers, including their unique identifiers and names
-- 25 rows, primary key: (id)
CREATE TABLE publisher (
-- Unique identifier for the publisher, ranging from 1 to 25
-- Stats: 0% null 100% unique
-- Foreign keys: superhero.publisher_id (one-to-many)
id integer,
-- Name of the publisher. Examples include 'Wildstorm', 'Universal Studios', 'Titan Books', 'Team Epic TV', 'SyFy'
-- Stats: 0% null 100% unique
publisher_name text
);
-- A table containing various superhero races or species, each with a unique identifier
-- 61 rows, primary key: (id)
CREATE TABLE race (
-- Unique identifier for the race, ranging from 1 to 61
-- Stats: 0% null 100% unique
-- Foreign keys: superhero.race_id (one-to-many)
id integer,
-- Superhero race or species. Sample values include 'Zombie', 'Zen-Whoberian', 'Yoda's species', 'Yautja', 'Xenomorph XX121'
-- Stats: 0% null 100% unique
race text
);
-- Comprehensive database of superhero information including physical attributes, identities, and affiliations
-- 750 rows, primary key: (id)
CREATE TABLE superhero (
-- Unique identifier for each superhero, ranging from 1 to 756
-- Stats: 0% null 100% unique
-- Foreign keys: hero_attribute.hero_id (one-to-many), hero_power.hero_id (one-to-many)
id integer,
-- Superhero alias, e.g. 'Atlas', 'Chameleon', 'Captain Marvel'
-- Stats: 0% null 99.1% unique
superhero_name text,
-- Real name of the superhero. Typically consists of given name and surname. '-' indicates unknown. E.g. 'Richard John Grayson', 'Bartholomew Allen II'
-- Stats: 16.3% null 64.4% unique
full_name text,
-- Identifier for superhero's gender, values range from 1 to 3
-- Stats: 0% null 0.4% unique
-- Foreign keys: gender.id (many-to-one)
gender_id integer,
-- Identifier for superhero's eye color, values range from 1 to 35
-- Stats: 0% null 2.8% unique
-- Foreign keys: colour.id (many-to-one)
eye_colour_id integer,
-- See eye_colour_id
-- Stats: 0% null 3.47% unique
-- Foreign keys: colour.id (many-to-one)
hair_colour_id integer,
-- See eye_colour_id
-- Stats: 0% null 2.13% unique
-- Foreign keys: colour.id (many-to-one)
skin_colour_id integer,
-- Identifier for superhero's race, values range from 1 to 61
-- Stats: 0.533% null 8.13% unique
-- Foreign keys: race.id (many-to-one)
race_id integer,
-- Identifier for the superhero's publisher, values range from 1 to 25
-- Stats: 0.4% null 3.33% unique
-- Foreign keys: publisher.id (many-to-one)
publisher_id integer,
-- Identifier for superhero's alignment (e.g. good, evil, neutral), values range from 1 to 3
-- Stats: 0.8% null 0.4% unique
-- Foreign keys: alignment.id (many-to-one)
alignment_id integer,
-- Height of the superhero in centimeters. 0 or NULL indicates missing data. Values range from 0 to 30480
-- Stats: 7.73% null 7.33% unique
height_cm integer,
-- Weight of the superhero in kilograms. 0 or NULL indicates missing data. Values range from 0 to 90000000
-- Stats: 8.53% null 18.7% unique
weight_kg integer
);
-- Links superheroes to their attribute scores, providing a quantitative measure of various superhero capabilities
-- 3738 rows
CREATE TABLE hero_attribute (
-- Unique identifier for a superhero, ranging from 1 to 756
-- Stats: 0% null 16.7% unique
-- Foreign keys: superhero.id (many-to-one)
hero_id integer,
-- Identifier for a superhero attribute, ranging from 1 to 6
-- Stats: 0% null 0.161% unique
-- Foreign keys: attribute.id (many-to-one)
attribute_id integer,
-- Numeric value representing the level or strength of an attribute for a superhero, ranging from 5 to 100. Higher values indicate greater skill or power in that attribute.
-- Stats: 0% null 0.535% unique
attribute_value integer
);
-- A comprehensive list of superpowers, each with a unique identifier and name
-- 167 rows, primary key: (id)
CREATE TABLE superpower (
-- Unique identifier for each superpower, ranging from 1 to 167
-- Stats: 0% null 100% unique
-- Foreign keys: hero_power.power_id (one-to-many)
id integer,
-- Name of the superpower, e.g. 'Wind Control', 'Web Creation', 'Weather Control'
-- Stats: 0% null 100% unique
power_name text
);
-- Junction table linking superheroes to their superpowers
-- 5825 rows
CREATE TABLE hero_power (
-- Foreign key referencing superhero(id). Integer values ranging from 1 to 756.
-- Stats: 0% null 11.2% unique
-- Foreign keys: superhero.id (many-to-one)
hero_id integer,
-- Foreign key referencing superpower(id). Integer values ranging from 1 to 167. Represents specific abilities used by superheroes to fight crime and protect others.
-- Stats: 0% null 2.87% unique
-- Foreign keys: superpower.id (many-to-one)
power_id integer
);