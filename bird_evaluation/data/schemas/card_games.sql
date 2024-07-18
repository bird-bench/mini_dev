-- A table containing detailed information about Magic: The Gathering cards, including their attributes, game mechanics, and printing details
-- 56822 rows, primary key: (id)
CREATE TABLE cards (
-- Unique id number identifying the cards
-- Stats: 0% null 100% unique
id integer,
-- The name of the artist that illustrated the card art
-- Stats: 0.00528% null 1.74% unique
artist text,
-- The ASCII (Basic/128) code formatted card name with no special unicode characters
-- Stats: 99.9% null 0.0458% unique
asciiName text,
-- A list of the card's available printing types. Values: "arena", "dreamcast", "mtgo", "paper", "shandalar"
-- Stats: 0.00176% null 0.0158% unique
availability text,
-- The color of the card border. Values: "black", "borderless", "gold", "silver", "white"
-- Stats: 0% null 0.0088% unique
borderColor text,
-- See cardKingdomId
-- Stats: 49.1% null 50.9% unique
cardKingdomFoilId text,
-- A list of all the colors in the color indicator
-- Stats: 24% null 76% unique
cardKingdomId text,
-- A list of all the colors found in manaCost, colorIndicator, and text
-- Stats: 11% null 0.0546% unique
colorIdentity text,
-- A list of all the colors in the color indicator (The symbol prefixed to a card's types)
-- Stats: 99.7% null 0.0158% unique
colorIndicator text,
-- A list of all the colors in manaCost and colorIndicator. Some cards may not have values, such as cards with "Devoid" in its text
-- Stats: 22.1% null 0.0686% unique
colors text,
-- The converted mana cost of the card. Higher values mean the card costs more converted mana
-- Stats: 0% null 0.0334% unique
convertedManaCost real,
-- The indicator for which duel deck the card is in
-- Stats: 97.2% null 0.00352% unique
duelDeck text,
-- The card rank on EDHRec
-- Stats: 8.38% null 36.4% unique
edhrecRank integer,
-- The converted mana cost or mana value for the face for either half or part of the card. Higher values mean the card costs more converted mana for the face
-- Stats: 98.3% null 0.0141% unique
faceConvertedManaCost real,
-- The name on the face of the card
-- Stats: 97.6% null 1.07% unique
faceName text,
-- The promotional card name printed above the true card name on special cards that has no game function
-- Stats: 100% null 0.037% unique
flavorName text,
-- The italicized text found below the rules text that has no game function
-- Stats: 45.8% null 30.4% unique
flavorText text,
-- The visual frame effects. Values include "colorshifted", "companion", "compasslanddfc", "devoid", "draft", "etched", "extendedart", "fullart", "inverted", "legendary", "lesson", "miracle", "mooneldrazidfc", "nyxtouched", "originpwdfc", "showcase", "snow", "sunmoondfc", "textless", "tombstone", "waxingandwaningmoondfc"
-- Stats: 94.8% null 0.0634% unique
frameEffects text,
-- The version of the card frame style. Values: "1993", "1997", "2003", "2015", "future"
-- Stats: 0% null 0.0088% unique
frameVersion text,
-- The starting maximum hand size total modifier. A + or - character precedes an integer
-- Stats: 99.8% null 0.0141% unique
hand text,
-- If the card allows a value other than 4 copies in a deck. 0: disallow, 1: allow
-- Stats: 0% null 0.00352% unique
hasAlternativeDeckLimit integer,
-- If the card is marked by Wizards of the Coast for having sensitive content. 0: doesn't have, 1: has sensitive content
-- Stats: 0% null 0.00352% unique
hasContentWarning integer,
-- If the card can be found in foil. 0: cannot be found, 1: can be found
-- Stats: 0% null 0.00352% unique
hasFoil integer,
-- If the card can be found in non-foil. 0: cannot be found, 1: can be found
-- Stats: 0% null 0.00352% unique
hasNonFoil integer,
-- If the card is an alternate variation to an original printing. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isAlternative integer,
-- If the card has full artwork. 0: doesn't have, 1: has full artwork
-- Stats: 0% null 0.00352% unique
isFullArt integer,
-- If the card is only available in online game variations. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isOnlineOnly integer,
-- If the card is oversized. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isOversized integer,
-- If the card is a promotional printing. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isPromo integer,
-- If the card has been reprinted. 0: has not, 1: has been
-- Stats: 0% null 0.00352% unique
isReprint integer,
-- If the card is on the Magic: The Gathering Reserved List. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isReserved integer,
-- If the card is found in a starter deck such as Planeswalker/Brawl decks. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isStarter integer,
-- If the card is a Story Spotlight card. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isStorySpotlight integer,
-- If the card does not have a text box. 0: has a text box, 1: doesn't have a text box
-- Stats: 0% null 0.00352% unique
isTextless integer,
-- If the card is "timeshifted", a feature of certain sets where a card will have a different frameVersion. 0: is not, 1: is
-- Stats: 0% null 0.00352% unique
isTimeshifted integer,
-- A list of keywords found on the card
-- Stats: 63.7% null 2.04% unique
keywords text,
-- The type of card layout. For a token card, this will be "token"
-- Stats: 0% null 0.0264% unique
layout text,
-- A list of formats the card is legal to be a commander in
-- Stats: 93.4% null 0.0088% unique
leadershipSkills text,
-- The starting life total modifier. A plus or minus character precedes an integer
-- Stats: 99.8% null 0.0405% unique
life text,
-- The starting loyalty value of the card. Used only on cards with "Planeswalker" in its types. Empty means unknown
-- Stats: 98.5% null 0.0194% unique
loyalty text,
-- The mana cost of the card wrapped in brackets for each value. Represents unconverted mana cost
-- Stats: 12.9% null 1.22% unique
manaCost text,
-- NOT USEFUL
-- Stats: 14.1% null 84.4% unique
mcmId text,
-- NOT USEFUL
-- Stats: 31.5% null 36.8% unique
mcmMetaId text,
-- NOT USEFUL
-- Stats: 89.7% null 9.95% unique
mtgArenaId text,
-- NOT USEFUL
-- Stats: 0% null 100% unique
mtgjsonV4Id text,
-- NOT USEFUL
-- Stats: 57.1% null 42.7% unique
mtgoFoilId text,
-- NOT USEFUL
-- Stats: 43.4% null 56% unique
mtgoId text,
-- NOT USEFUL
-- Stats: 26% null 73.7% unique
multiverseId text,
-- The name of the card. Cards with multiple faces, like "Split" and "Meld" cards are given a delimiter
-- Stats: 0% null 38.3% unique
name text,
-- The number of the card
-- Stats: 0% null 11.7% unique
"number" text,
-- The original release date in ISO 8601 format for a promotional card printed outside of a cycle window, such as Secret Lair Drop promotions
-- Stats: 96.4% null 0.674% unique
originalReleaseDate text,
-- The text on the card as originally printed
-- Stats: 27.5% null 48.6% unique
originalText text,
-- The type of the card as originally printed. Includes any supertypes and subtypes
-- Stats: 26% null 5.27% unique
originalType text,
-- A list of card UUID's to this card's counterparts, such as transformed or melded faces
-- Stats: 97.6% null 2.4% unique
otherFaceIds text,
-- The power of the card. ∞ means infinite power, null or * refers to unknown power
-- Stats: 53.9% null 0.0493% unique
power text,
-- A list of set printing codes the card was printed in, formatted in uppercase
-- Stats: 0% null 11% unique
printings text,
-- A list of promotional types for a card. Values include "arenaleague", "boosterfun", "boxtopper", "brawldeck", "bundle", "buyabox", "convention", "datestamped", "draculaseries", "draftweekend", "duels", "event", "fnm", "gameday", "gateway", "giftbox", "gilded", "godzillaseries", "instore", "intropack", "jpwalker", "judgegift", "league", "mediainsert", "neonink", "openhouse", "planeswalkerstamped", "playerrewards", "playpromo", "premiereshop", "prerelease", "promopack", "release", "setpromo", "stamped", "textured", "themepack", "thick", "tourney", "wizardsplaynetwork"
-- Stats: 89.2% null 0.113% unique
promoTypes text,
-- Links that navigate to websites where the card can be purchased
-- Stats: 11.2% null 88.8% unique
purchaseUrls text,
-- The card printing rarity
-- Stats: 0% null 0.00704% unique
rarity text,
-- NOT USEFUL
-- Stats: 0% null 98.8% unique
scryfallId text,
-- NOT USEFUL
-- Stats: 0.00352% null 48% unique
scryfallIllustrationId text,
-- NOT USEFUL
-- Stats: 0% null 38.3% unique
scryfallOracleId text,
-- The set printing code that the card is from
-- Stats: 0% null 0.943% unique
setCode text,
-- The identifier of the card side. Used on cards with multiple faces on the same card. Empty value means the card doesn't have multiple faces on the same card
-- Stats: 97.6% null 0.0088% unique
side text,
-- A list of card subtypes found after em-dash
-- Stats: 39.1% null 2.65% unique
subtypes text,
-- A list of card supertypes found before em-dash
-- Stats: 86.2% null 0.0141% unique
supertypes text,
-- Stats: 11.6% null 87.1% unique
tcgplayerProductId text,
-- The rules text of the card
-- Stats: 1.68% null 36.2% unique
"text" text,
-- The toughness of the card
-- Stats: 53.9% null 0.0563% unique
toughness text,
-- The type of the card as visible, including any supertypes and subtypes. Values include "Artifact", "Card", "Conspiracy", "Creature", "Dragon", "Dungeon", "Eaturecray", "Elemental", "Elite", "Emblem", "Enchantment", "Ever", "Goblin", "Hero", "Instant", "Jaguar", "Knights", "Land", "Phenomenon", "Plane", "Planeswalker", "Scariest", "Scheme", "See", "Sorcery", "Sticker", "Summon", "Token", "Tribal", "Vanguard", "Wolf", "You'll", "instant"
-- Stats: 0% null 3.56% unique
type text,
-- A list of all card types of the card, including Un‑sets and gameplay variants
-- Stats: 0% null 0.0651% unique
types text,
-- The universal unique identifier (v5) generated by MTGJSON. Each entry is unique
-- Stats: 0% null 100% unique
-- Foreign keys: foreign_data.uuid (one-to-many), legalities.uuid (one-to-many), rulings.uuid (one-to-many)
"uuid" text,
-- Stats: 84.8% null 14.5% unique
variations text,
-- The name of the watermark on the card
-- Stats: 92.2% null 0.283% unique
watermark text
);
-- Contains information about Magic: The Gathering cards in various foreign languages, including translations of card names, types, rules text, and flavor text
-- 229186 rows, primary key: (id)
CREATE TABLE foreign_data (
-- Unique identifier for each row, ranging from 1 to 229205
-- Stats: 0% null 100% unique
id integer,
-- The flavor text of the card in various foreign languages. Can be empty. Examples: '文明の手による介入がなければ、自然は必ずその必要に応じて自らを変容させる。', 'Tutte le semi condividono un legame comune, chiamandosi l'un l'altro nello spazio infinito.'
-- Stats: 0% null 48.5% unique
flavorText text,
-- The language of the card text. Examples: 'Japanese', 'French', 'German', 'Italian', 'Spanish'
-- Stats: 0% null 0.00698% unique
language text,
-- Unique identifier for each foreign version of a card, ranging from 73246 to 507640
-- Stats: 16.8% null 82.2% unique
multiverseid integer,
-- The name of the card in the foreign language. Examples: 'Pacifismo', 'Naturalizar', 'Trial // Error', 'Desencantar', '心之衰'
-- Stats: 0% null 70.1% unique
name text,
-- The rules text of the card in the foreign language. Can be empty. Examples: '飛行', 'Fliegend', 'Vol', '飞行', 'Vuela.'
-- Stats: 0% null 70.4% unique
"text" text,
-- The card type in the foreign language, including supertypes and subtypes. Can be empty. Examples: 'Spontanzauber', 'Hexerei', 'インスタント', 'Éphémère', 'Istantaneo'
-- Stats: 0% null 7.23% unique
type text,
-- See id
-- Stats: 0% null 14.9% unique
-- Foreign keys: cards.uuid (many-to-one)
"uuid" text
);
-- Contains information about the legality of cards in various game formats
-- 427907 rows, primary key: (id)
CREATE TABLE legalities (
-- Unique identifier for each legality entry, ranging from 1 to 427907
-- Stats: 0% null 100% unique
id integer,
-- Format of play, referring to different rules. Examples include 'vintage', 'legacy', 'commander', 'duel', 'modern', etc.
-- Stats: 0% null 0.00351% unique
"format" text,
-- Legality status. Values are 'Legal', 'Banned', or 'Restricted'
-- Stats: 0% null 0.000701% unique
status text,
-- Unique identifier in UUID format
-- Stats: 0% null 13% unique
-- Foreign keys: cards.uuid (many-to-one)
"uuid" text
);
-- A comprehensive table of Magic: The Gathering card sets, including various attributes such as release dates, set sizes, and distribution details
-- 551 rows, primary key: (id)
CREATE TABLE sets (
-- Unique identifier for each set, ranging from 1 to 551
-- Stats: 0% null 100% unique
id integer,
-- The number of cards in the set, ranging from 0 to 1694
-- Stats: 0% null 30.1% unique
baseSetSize integer,
-- The block name the set was in, e.g. 'Core Set', 'Commander', 'Theros'
-- Stats: 50.6% null 5.99% unique
block text,
-- JSON-formatted breakdown of card possibilities and weights in a booster pack
-- Stats: 75% null 15.4% unique
booster text,
-- The set code, e.g. '10E', '2ED', '2XM'
-- Stats: 0% null 100% unique
-- Foreign keys: set_translations.setCode (one-to-many)
code text,
-- Boolean (0 or 1) indicating if the set is only available in foil
-- Stats: 0% null 0.363% unique
isFoilOnly integer,
-- Boolean (0 or 1) indicating if the set is available only outside the USA
-- Stats: 0% null 0.363% unique
isForeignOnly integer,
-- Boolean (0 or 1) indicating if the set is only available in non-foil
-- Stats: 0% null 0.363% unique
isNonFoilOnly integer,
-- Boolean (0 or 1) indicating if the set is only available in online game variations
-- Stats: 0% null 0.363% unique
isOnlineOnly integer,
-- Boolean (0 or 1) indicating if the set is still in preview (spoiled)
-- Stats: 0% null 0.363% unique
isPartialPreview integer,
-- The matching Keyrune code for set image icons, e.g. 'PMEI', 'ZNR', 'MTGA'
-- Stats: 0% null 45.2% unique
keyruneCode text,
-- The Magic Card Market set identifier, ranging from 4 to 3660
-- Stats: 63.5% null 36.5% unique
mcmId integer,
-- The split Magic Card Market set identifier for the second set, if printed in two sets
-- Stats: 98.2% null 1.81% unique
mcmIdExtras integer,
-- See mcmId
-- Stats: 63.5% null 36.5% unique
mcmName text,
-- The set code for Magic: The Gathering Online. Null or empty if not on MTGO
-- Stats: 71% null 29% unique
mtgoCode text,
-- See id
-- Stats: 0% null 100% unique
name text,
-- The parent set code for set variations like promotions, guild kits, etc.
-- Stats: 72.1% null 21.2% unique
parentCode text,
-- The release date in ISO 8601 format (YYYY-MM-DD)
-- Stats: 0% null 62.1% unique
releaseDate date,
-- The group identifier of the set on TCGplayer, ranging from 1 to 2778
-- Stats: 52.8% null 43.2% unique
tcgplayerGroupId integer,
-- Total number of cards including promotional and supplemental products, excluding Alchemy modifications
-- Stats: 0% null 32.8% unique
totalSetSize integer,
-- The expansion type, e.g. 'alchemy', 'archenemy', 'arsenal', 'box', 'commander', 'core', 'expansion', 'funny'
-- Stats: 0% null 3.63% unique
type text
);
-- Contains translations of Magic: The Gathering card set names in various languages, including set codes and unique identifiers
-- 1210 rows, primary key: (id)
CREATE TABLE set_translations (
-- Unique identifier for each set translation, ranging from 1 to 1210
-- Stats: 0% null 100% unique
id integer,
-- Language of the card set translation. Sample values include 'Spanish', 'Russian', 'Portuguese (Brazil)', 'Korean', 'Japanese', 'Italian', 'German', 'French', 'Chinese Traditional', 'Chinese Simplified'
-- Stats: 0% null 0.826% unique
language text,
-- Set code for the card set. Contains 121 unique codes, ranging from '10E' to 'WTH'. Sample values include 'WTH', 'WAR', 'V16', 'V15', 'V14'
-- Stats: 0% null 10% unique
-- Foreign keys: sets.code (many-to-one)
setCode text,
-- Translated name of the card set. Contains 504 unique translations. Sample values include 'Venser vs. Koth', 'Tempest Remastered', 'Speed vs. Cunning', 'Sorin vs. Tibalt', 'Premium Deck Series: Fire & Lightning'
-- Stats: 19.1% null 41.7% unique
translation text
);
-- A comprehensive collection of rulings for a card game, including unique identifiers, dates, and detailed explanations
-- 87769 rows, primary key: (id)
CREATE TABLE rulings (
-- Unique identifier for each ruling, ranging from 1 to 87769
-- Stats: 0% null 100% unique
id integer,
-- Date of the ruling in YYYY-MM-DD format, ranging from 2004-10-04 to 2021-02-05
-- Stats: 0% null 0.124% unique
"date" date,
-- Detailed description of the ruling, often explaining game mechanics or card interactions
-- Stats: 0% null 22.3% unique
"text" text,
-- Unique identifier in UUID format, e.g. 'f2ef8f0a-ea29-5750-9f86-f4ee22b1af7e'
-- Stats: 0% null 29.8% unique
-- Foreign keys: cards.uuid (many-to-one)
"uuid" text
);