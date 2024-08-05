import glob
import yaml
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# First read all metadata.yml files in assay into Pandas dataframe

yml_files = glob.glob(f"{os.environ['PROJECT_HOME']}/assays/*/*.yml", recursive=True)

metadata_dict = {}
for file in yml_files:
    assay_path = os.path.dirname(os.path.realpath(file))
    with open(file, "r") as f:
        contents = yaml.safe_load(f)
    if assay_path in metadata_dict:
        metadata_dict[assay_path].update(contents)
    else:
        metadata_dict[assay_path] = contents

# Check all assays used latest cruft schema version

metadata = pd.DataFrame.from_dict(metadata_dict, orient="index")

# Check all assays use correct metadata schema version

if not metadata['schema_version'].nunique() == 1:
    raise ValueError("First run cruft update on assays")

metadata = metadata[["assay_id", "assay", "owner", "date", "eln_id", "technology", "sequencer", "seq_kit",
"n_samples", "is_paired", "pipeline", "processed_by", "organism", "organism_version", "organism_subgroup",
"origin", "short_desc", "long_desc", "note", "genomics_path"]]

# Some checks

# print(list(metadata.columns))
# metadata.to_csv('db/metadata.csv', sep='\t', index=False)


# Connect to SQLite database

connection = sqlite3.connect("db/ngs_catalogue.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()


# Insert data into database

## sequencing_kits
kits = list(set(metadata[["seq_kit"]].itertuples(index=False, name=None)))
cursor.executemany("INSERT INTO sequencing_kits (kit) VALUES(?)", kits)

## sequencers
seq = list(set(metadata[["sequencer"]].itertuples(index=False, name=None)))
cursor.executemany("INSERT INTO sequencers (model) VALUES(?)", seq)

## users
usr = list(set(metadata[["owner"]].itertuples(index=False, name=None))) + list(
    set(metadata[["processed_by"]].itertuples(index=False, name=None))
)
cursor.executemany("INSERT INTO users (first_last_name) VALUES(?)", usr)
update = """UPDATE users SET department = 'Genomics Core' WHERE first_last_name='Magali Michaut' OR first_last_name='Adrija Kalvisa' """
cursor.execute(update)

## pipelines
pline = list(set(metadata[["pipeline"]].itertuples(index=False, name=None)))
cursor.executemany("INSERT INTO pipelines (pipeline_name) VALUES(?)", pline)

## assay
data = list(metadata.itertuples(index=False, name=None))

cursor.executemany("""
    INSERT INTO assay
    (id, assay, owner_id, created_on, eln_id, technology,
    sequencer_id, seq_kit_id, n_samples, is_paired, pipeline_id, processed_by_id,
    organism, organism_version, organism_subgroup, origin, short_desc, long_desc, note, genomics_path)
    VALUES(
        ?,
        ?,
        (SELECT user_id FROM users WHERE first_last_name=?),
        ?,
        ?,
        ?,
        (SELECT seq_id FROM sequencers WHERE model = ?),
        (SELECT seq_id FROM sequencing_kits WHERE kit = ?),
        ?,
        ?,
        (SELECT pipeline_id FROM pipelines WHERE pipeline_name = ?),
        (SELECT user_id FROM users WHERE first_last_name=?),
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?)
        """,
    data,
)


## Close connection

connection.commit()
cursor.close()
connection.close()
