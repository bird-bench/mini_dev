-- Contains information about atoms in molecules, including their unique identifiers, the molecules they belong to, and their chemical elements.
-- 9111 rows, primary key: (atom_id)
CREATE TABLE atom (
-- Unique identifier for atoms, following the format TRXXX_Y where XXX is the molecule number and Y is the atom number within that molecule. Range: TR000_1 to TR501_9.
-- Stats: 0% null 100% unique
-- Foreign keys: connected.atom_id2 (one-to-many), connected.atom_id (one-to-many)
atom_id text,
-- Identifier for the molecule to which the atom belongs, in the format TRXXX where XXX is a number. Range: TR000 to TR501.
-- Stats: 0% null 3.76% unique
-- Foreign keys: molecule.molecule_id (many-to-one)
molecule_id text,
-- Chemical element of the atom, represented by its symbol. Includes: cl (chlorine), c (carbon), h (hydrogen), o (oxygen), s (sulfur), n (nitrogen), p (phosphorus), na (sodium), br (bromine), f (fluorine), i (iodine), sn (Tin), pb (lead), te (tellurium), ca (Calcium), and others.
-- Stats: 0% null 0.198% unique
element text
);
-- Chemical bond information for molecules, including bond identifiers, molecule associations, and bond types
-- 9156 rows, primary key: (bond_id)
CREATE TABLE bond (
-- Unique identifier for bonds in format TRxxx_A1_A2, where TRxxx refers to the molecule, A1 and A2 refer to the connected atoms. Sample values: 'TR000_1_2', 'TR001_10_11'
-- Stats: 0% null 100% unique
-- Foreign keys: connected.bond_id (one-to-many)
bond_id text,
-- Identifier for the molecule containing the bond. Format: TRxxx. Range: TR000 to TR501
-- Stats: 0% null 3.75% unique
-- Foreign keys: molecule.molecule_id (many-to-one)
molecule_id text,
-- Type of chemical bond. Values: '-' (single bond), '=' (double bond), '#' (triple bond)
-- Stats: 0% null 0.0328% unique
bond_type text
);
-- Table representing connections between atoms, storing information about atom pairs and their corresponding bonds.
-- 18312 rows, primary key: (atom_id, atom_id2)
CREATE TABLE connected (
-- Unique identifier for the first atom in a bond, following the format 'TRxxx_y' where xxx is a three-digit number and y is a single digit.
-- Stats: 0% null 49.5% unique
-- Foreign keys: atom.atom_id (many-to-one)
atom_id text,
-- See atom_id. Represents the second atom in a bond.
-- Stats: 0% null 49.5% unique
-- Foreign keys: atom.atom_id (many-to-one)
atom_id2 text,
-- Unique identifier for the bond between two atoms, following the format 'TRxxx_y_z' where xxx, y, and z are numbers.
-- Stats: 0% null 50% unique
-- Foreign keys: bond.bond_id (many-to-one)
bond_id text
);
-- A table containing information about molecules and their carcinogenic properties, with unique identifiers and binary labels.
-- 343 rows, primary key: (molecule_id)
CREATE TABLE molecule (
-- Unique ID of molecule. Format: 'TR' followed by a three-digit number (e.g. 'TR000', 'TR501'). '+' indicates the molecule/compound is carcinogenic, '-' indicates it is not carcinogenic.
-- Stats: 0% null 100% unique
-- Foreign keys: atom.molecule_id (one-to-many), bond.molecule_id (one-to-many)
molecule_id text,
-- Binary indicator of carcinogenicity: '+' for carcinogenic, '-' for non-carcinogenic.
-- Stats: 0% null 0.583% unique
label text
);