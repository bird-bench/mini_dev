-- Records of badges awarded to users, including badge details and award timestamps
-- 79851 rows, primary key: (Id)
CREATE TABLE badges (
-- Unique badge identifier, ranging from 1 to 92240
-- Stats: 0% null 100% unique
Id integer,
-- Unique user identifier, ranging from 2 to 55746
-- Stats: 0% null 31.4% unique
-- Foreign keys: users.Id (many-to-one)
UserId integer,
-- Badge name awarded to the user. Examples include 'Student', 'Supporter', 'Editor', 'Scholar', 'Teacher'
-- Stats: 0% null 0.192% unique
Name text,
-- Timestamp of badge award, in format 'YYYY-MM-DD HH:MM:SS.S', ranging from '2010-07-19 19:39:07.0' to '2014-09-14 02:31:28.0'
-- Stats: 0% null 82.1% unique
"Date" datetime
);
-- Table containing user comments on posts, including metadata such as scores, creation dates, and user information
-- 174285 rows, primary key: (Id)
CREATE TABLE comments (
-- Unique identifier for each comment
-- Stats: 0% null 100% unique
Id integer,
-- Unique identifier of the associated post
-- Stats: 0% null 30.6% unique
-- Foreign keys: posts.Id (many-to-one)
PostId integer,
-- Rating score from 0 to 90. Scores above 60 indicate positive comments, below 60 indicate negative comments.
-- Stats: 0% null 0.0207% unique
Score integer,
-- Detailed content of the comment
-- Stats: 0% null 99.6% unique
"Text" text,
-- Timestamp of comment creation in 'YYYY-MM-DD HH:MM:SS.S' format
-- Stats: 0% null 99.9% unique
CreationDate datetime,
-- Identifier of the user who posted the comment
-- Stats: 1.63% null 7.83% unique
-- Foreign keys: users.Id (many-to-one)
UserId integer,
-- Display name of the user, often in format 'userXXXXX' where X is a number
-- Stats: 98.4% null 0.531% unique
UserDisplayName text
);
-- Tracks the revision history of posts, including edits to content, tags, and titles, along with user information and timestamps.
-- 303155 rows, primary key: (Id)
CREATE TABLE postHistory (
-- Unique identifier for each post history entry. Integer values ranging from 1 to 386848.
-- Stats: 0% null 100% unique
Id integer,
-- Identifier for the type of post history. Integer values from 1 to 38, with 25 unique types.
-- Stats: 0% null 0.00825% unique
PostHistoryTypeId integer,
-- Unique identifier for the associated post. Integer values from 1 to 115378.
-- Stats: 0% null 30.3% unique
-- Foreign keys: posts.Id (many-to-one)
PostId integer,
-- Globally unique identifier for each revision. Format: 8-4-4-4-12 hexadecimal characters, e.g., '6887d756-76f7-4279-bd02-adccbc90ac17'.
-- Stats: 0% null 64% unique
RevisionGUID text,
-- Timestamp of the post history entry. Format: 'YYYY-MM-DD HH:MM:SS.0', ranging from '2009-02-02 14:21:12.0' to '2014-09-14 02:54:13.0'.
-- Stats: 0% null 62.7% unique
CreationDate datetime,
-- Identifier of the user who made the post. Integer values from -1 to 55746, where -1 might indicate an anonymous or system user.
-- Stats: 7.03% null 7.29% unique
-- Foreign keys: users.Id (many-to-one)
UserId integer,
-- Detailed content of the post. Can include empty strings, HTML tags, JSON data, or various text content.
-- Stats: 0% null 84% unique
"Text" text,
-- Brief description of the changes made. Often includes phrases like 'edited title', 'edited tags', 'edited body', or specific character count changes.
-- Stats: 0% null 14.3% unique
"Comment" text,
-- Display name of the user. Can be empty, 'userXXXXX' format, or custom names. Some special characters may be present.
-- Stats: 0% null 0.383% unique
UserDisplayName text
);
-- Contains information about links between posts, including their creation dates and types.
-- 11102 rows, primary key: (Id)
CREATE TABLE postLinks (
-- Unique identifier for each post link. Integer values ranging from 108 to 3356789.
-- Stats: 0% null 100% unique
Id integer,
-- Timestamp of when the post link was created, in the format 'YYYY-MM-DD HH:MM:SS.S'. Range from '2010-07-21 14:47:33.0' to '2014-09-13 20:54:31.0'.
-- Stats: 0% null 85.1% unique
CreationDate datetime,
-- Identifier of the post. Integer values ranging from 4 to 115360.
-- Stats: 0% null 68.5% unique
-- Foreign keys: posts.Id (many-to-one)
PostId integer,
-- Identifier of the related post. Integer values ranging from 1 to 115163.
-- Stats: 0% null 46.6% unique
-- Foreign keys: posts.Id (many-to-one)
RelatedPostId integer,
-- Type of link between posts. Integer values: 1 or 3.
-- Stats: 0% null 0.018% unique
LinkTypeId integer
);
-- A comprehensive table containing information about posts, including their metadata, content, and user interactions
-- 91966 rows, primary key: (Id)
CREATE TABLE posts (
-- Unique post identifier, ranging from 1 to 115378
-- Stats: 0% null 100% unique
-- Foreign keys: comments.PostId (one-to-many), postHistory.PostId (one-to-many), postLinks.RelatedPostId (one-to-many), postLinks.PostId (one-to-many), posts.ParentId (one-to-many), tags.ExcerptPostId (one-to-one), votes.PostId (one-to-many)
Id integer,
-- Type of post, values range from 1 to 7
-- Stats: 0% null 0.00761% unique
PostTypeId integer,
-- ID of the accepted answer for the post, if applicable
-- Stats: 84% null 16% unique
AcceptedAnswerId integer,
-- Date and time when the post was created, format: 'YYYY-MM-DD HH:MM:SS.0', ranging from 2009-02-02 to 2014-09-14
-- Stats: 0% null 99.2% unique
CreaionDate datetime,
-- Post score, ranging from -19 to 192
-- Stats: 0% null 0.141% unique
Score integer,
-- Number of times the post has been viewed. Higher view count means the post has higher popularity. Range: 1 to 175495
-- Stats: 53.3% null 4.04% unique
ViewCount integer,
-- Content of the post
-- Stats: 0.239% null 99.7% unique
Body text,
-- User ID of the post owner, ranging from -1 to 55746
-- Stats: 1.51% null 23.9% unique
-- Foreign keys: users.Id (many-to-one)
OwnerUserId integer,
-- Date and time of the last activity on the post, format: 'YYYY-MM-DD HH:MM:SS.0', ranging from 2009-02-02 to 2014-09-14
-- Stats: 0% null 79% unique
LasActivityDate datetime,
-- Title of the post
-- Stats: 53.3% null 46.6% unique
Title text,
-- Tags associated with the post, format: '<tag1><tag2>...'
-- Stats: 53.3% null 31% unique
Tags text,
-- Number of answers to the post, ranging from 0 to 136
-- Stats: 53.3% null 0.0337% unique
AnswerCount integer,
-- Number of comments on the post, ranging from 0 to 45
-- Stats: 0% null 0.0424% unique
CommentCount integer,
-- Number of times the post was favorited. More favorite count refers to more valuable posts. Range: 0 to 233
-- Stats: 85.6% null 0.0837% unique
FavoriteCount integer,
-- User ID of the last editor, ranging from -1 to 55733
-- Stats: 51.5% null 7.15% unique
-- Foreign keys: users.Id (many-to-one)
LastEditorUserId integer,
-- Date and time of the last edit, format: 'YYYY-MM-DD HH:MM:SS.0', ranging from 2010-07-19 to 2014-09-14
-- Stats: 51% null 48.8% unique
LastEditDate datetime,
-- Date and time when the post became community owned, if applicable. Format: 'YYYY-MM-DD HH:MM:SS.0', ranging from 2010-07-19 to 2014-09-11
-- Stats: 97.3% null 2.11% unique
CommunityOwnedDate datetime,
-- ID of the parent post. If null, the post is a root post; otherwise, it's a child post. Range: 1 to 115375
-- Stats: 48.1% null 31.5% unique
-- Foreign keys: posts.Id (many-to-one)
ParentId integer,
-- Date and time when the post was closed, if applicable. If null or empty, the post is not well-finished; otherwise, it is well-finished. Format: 'YYYY-MM-DD HH:MM:SS.0', ranging from 2010-07-19 to 2014-09-13
-- Stats: 98.2% null 1.75% unique
ClosedDate datetime,
-- Display name of the post owner
-- Stats: 97.3% null 1.75% unique
OwnerDisplayName text,
-- Display name of the last editor
-- Stats: 99.5% null 0.0642% unique
LastEditorDisplayName text
);
-- A comprehensive list of tags used in a Q&A or forum-like platform, including their usage statistics and associated post IDs
-- 1032 rows, primary key: (Id)
CREATE TABLE tags (
-- The tag ID, ranging from 1 to 1869
-- Stats: 0% null 100% unique
Id integer,
-- The name of the tag, alphabetically ordered from '2sls' to 'zipf'
-- Stats: 0% null 100% unique
TagName text,
-- Number of posts containing this tag. More counts indicate higher tag popularity. Range: 1 to 7244
-- Stats: 0% null 26.4% unique
Count integer,
-- The excerpt post ID of the tag, ranging from 2331 to 114058
-- Stats: 42.2% null 57.8% unique
-- Foreign keys: posts.Id (one-to-one)
ExcerptPostId integer,
-- See ExcerptPostId. Range: 2254 to 114057
-- Stats: 42.2% null 57.8% unique
WikiPostId integer
);
-- User information table for a Q&A platform, including demographics, activity metrics, and account details
-- 40325 rows, primary key: (Id)
CREATE TABLE users (
-- Unique user identifier ranging from -1 to 55747
-- Stats: 0% null 100% unique
-- Foreign keys: badges.UserId (one-to-many), comments.UserId (one-to-many), postHistory.UserId (one-to-many), posts.OwnerUserId (one-to-many), posts.LastEditorUserId (one-to-many), votes.UserId (one-to-many)
Id integer,
-- User's reputation score ranging from 1 to 87393. Higher reputation indicates more influence.
-- Stats: 0% null 2.39% unique
Reputation integer,
-- Timestamp of account creation, ranging from '2010-07-19 06:55:26.0' to '2014-09-14 01:01:44.0'
-- Stats: 0% null 100% unique
CreationDate datetime,
-- User's chosen display name
-- Stats: 0% null 88.4% unique
DisplayName text,
-- Timestamp of user's most recent access, ranging from '2010-07-19 06:55:26.0' to '2014-09-14 03:05:57.0'
-- Stats: 0% null 99.9% unique
LastAccessDate datetime,
-- URL of user's website, if provided. Common values include 'http://none', 'http://N/A', '-'
-- Stats: 79.9% null 19.3% unique
WebsiteUrl text,
-- User-provided location information
-- Stats: 71% null 6.11% unique
Location text,
-- User's self-introduction, often in HTML format (e.g., '<p>Student</p>')
-- Stats: 76.7% null 22.7% unique
AboutMe text,
-- Number of profile views, ranging from 0 to 20932
-- Stats: 0% null 0.898% unique
Views integer,
-- See Views
-- Stats: 0% null 0.823% unique
UpVotes integer,
-- See Views
-- Stats: 0% null 0.188% unique
DownVotes integer,
-- Unique account identifier ranging from -1 to 5027354
-- Stats: 0% null 100% unique
AccountId integer,
-- User's age, categorized as: teenager (13-18), adult (19-65), elder (> 65). Range: 13 to 94
-- Stats: 79.4% null 0.174% unique
Age integer,
-- URL of user's profile image, often from Gravatar or Google
-- Stats: 59.1% null 32.5% unique
ProfileImageUrl text
);
-- Records of votes cast on posts, including vote type, user, creation date, and associated bounty amounts
-- 38930 rows, primary key: (Id)
CREATE TABLE votes (
-- Unique identifier for each vote, ranging from 1 to 43538
-- Stats: 0% null 100% unique
Id integer,
-- ID of the post being voted on, ranging from 1 to 16921
-- Stats: 0% null 22% unique
-- Foreign keys: posts.Id (many-to-one)
PostId integer,
-- ID representing the type of vote, ranging from 1 to 16
-- Stats: 0% null 0.0257% unique
VoteTypeId integer,
-- Date when the vote was cast, in 'YYYY-MM-DD' format, ranging from '2010-07-19' to '2011-05-01'
-- Stats: 0% null 0.737% unique
CreationDate date,
-- ID of the user who cast the vote, ranging from 5 to 11954
-- Stats: 91.2% null 1.31% unique
-- Foreign keys: users.Id (many-to-one)
UserId integer,
-- Amount of bounty associated with the vote, possible values are 0, 25, 50, 100, 150, 200
-- Stats: 99.7% null 0.0154% unique
BountyAmount integer
);