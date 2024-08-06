-- Database setup (SQLite) for NGS catalogue
-- To create database run the following command
--   $ sqlite3 ngs_catalogue.db < database.sql
-- To generate PDF database install `eralchemy` and run below
--   $ eralchemy -i sqlite:///ngs_catalogue.db -o ngs_catalogue.pdf

CREATE TABLE assay (
    assay_id INTEGER PRIMARY KEY,
    id TEXT NOT NULL,
    assay TEXT NOT NULL,
    owner_id INT NOT NULL,
    created_on TEXT NOT NULL,
    eln_id TEXT,
    technology TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    sequencer_id INT,
    seq_kit_id INT,
    n_samples INTEGER NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    is_paired INTEGER NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    pipeline_id INT,    
    processed_by_id INT,    
    organism TEXT NOT NULL,
    organism_version TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    organism_subgroup TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",    
    origin TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    short_desc TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    long_desc TEXT,
    note TEXT,
    genomics_path TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",

    FOREIGN KEY(owner_id) REFERENCES users(user_id),
    FOREIGN KEY(seq_kit_id) REFERENCES sequencing_kits(seq_id),
    FOREIGN KEY(sequencer_id) REFERENCES sequencers(seq_id),
    FOREIGN KEY(processed_by_id) REFERENCES users(user_id),
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(pipeline_id)
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    first_last_name TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN",
    department TEXT NOT NULL ON CONFLICT REPLACE DEFAULT "Brickman"
);

CREATE TABLE sequencing_kits (
    seq_id INTEGER PRIMARY KEY,
    kit TEXT  NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN"
);

CREATE TABLE sequencers (
    seq_id INTEGER PRIMARY KEY,
    model TEXT  NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN"
);

CREATE TABLE pipelines (
    pipeline_id INTEGER PRIMARY KEY,
    pipeline_name TEXT  NOT NULL ON CONFLICT REPLACE DEFAULT "UNKNOWN"
);
