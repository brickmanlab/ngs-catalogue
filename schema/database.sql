-- Database setup (SQLite) for NGS catalogue
-- To create database run the following command
--   $ sqlite3 ngs_catalogue.db < database.sql
-- To generate PDF database install `eralchemy` and run below
--   $ eralchemy -i sqlite:///ngs_catalogue.db -o ngs_catalogue.pdf

CREATE TABLE assay (
    assay_id SERIAL NOT NULL PRIMARY KEY,
    owner_id INT NOT NULL,
    seq_kit_id INT NOT NULL,
    sequencer_id INT NOT NULL,
    processed_by_id INT NOT NULL,
    pipeline_id INT NOT NULL,
    organism TEXT NOT NULL,
    organism_sub_id INT NOT NULL,
    created_at TEXT NOT NULL,
    revised_at TEXT,
    revised_by INTEGER,
    origin TEXT DEFAULT "internal" NOT NULL,
    is_paired INTEGER NOT NULL,
    n_samples INTEGER NOT NULL,
    codename TEXT,
    short_desc TEXT NOT NULL,
    long_desc TEXT NOT NULL,
    genomics_path TEXT,

    FOREIGN KEY(owner_id) REFERENCES users(user_id),
    FOREIGN KEY(seq_kit_id) REFERENCES sequencing_kits(seq_id),
    FOREIGN KEY(sequencer_id) REFERENCES sequencers(seq_id),
    FOREIGN KEY(processed_by_id) REFERENCES users(user_id),
    FOREIGN KEY(pipeline_id) REFERENCES pipelines(pipeline_id),
    FOREIGN KEY(organism_sub_id) REFERENCES organism_subgroups(org_id),
    FOREIGN KEY(revised_by) REFERENCES users(user_id)
);

CREATE TABLE users (
    user_id SERIAL NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    first_last_name TEXT NOT NULL,
    department TEXT NOT NULL
);

CREATE TABLE sequencing_kits (
    seq_id SERIAL NOT NULL PRIMARY KEY,
    kit TEXT NOT NULL
);

CREATE TABLE sequencers (
    seq_id SERIAL NOT NULL,
    model TEXT NOT NULL
);

CREATE TABLE pipelines (
    pipeline_id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    link TEXT NOT NULL
);

CREATE TABLE organism_subgroups (
    org_id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    desc TEXT NOT NULL
);