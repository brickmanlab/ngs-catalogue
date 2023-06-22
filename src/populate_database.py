#%%
import glob
import yaml
import os
import pandas as pd
import sqlite3

# First read all metadata.yml files in assay into Pandas dataframe

#%%
#Pathlib could be faster solution than glob for large folders
#yml_files = glob.glob('~/Brickman/assays/**/*.yml', recursive=True)
yml_files = glob.glob('/home/sarahlu/Documents/GitHub/ngs-catalogue/assays/**/*.yml', recursive=True)
print(yml_files)


#%%
nested_dict = {}
for file in yml_files:
    assay_path = os.path.dirname(os.path.realpath(file))
    with open(file, 'r') as f:
        contents = yaml.safe_load(f)
    if assay_path in nested_dict:
        nested_dict[assay_path].update(contents)
    else:
        nested_dict[assay_path] = contents
print(nested_dict)

#%%
# Read into Pandas dataframe
metadata = pd.DataFrame.from_dict(nested_dict, orient='index')
metadata.head(50)


# Connect to SQLite database

#%%
connection = sqlite3.connect("../db/ngs_catalogue.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())


# Insert data into database

## sequencing_kits
# %%
kits = list(set(metadata[["seq_kit"]].itertuples(index=False, name=None)))
#print(kits)
cursor.executemany("INSERT INTO sequencing_kits (kit) VALUES(?)", kits)
for row in cursor.execute("SELECT seq_id, kit FROM sequencing_kits"):
    print(row)


## sequencers
#%%
seq = list(set(metadata[["sequencer"]].itertuples(index=False, name=None)))
cursor.executemany("INSERT INTO sequencers (model) VALUES(?)", seq)
for row in cursor.execute("SELECT seq_id, model FROM sequencers"):
    print(row)

## users
# %%
usr = list(set(metadata[["owner"]].itertuples(index=False, name=None))) + \
    list(set(metadata[["processed_by"]].itertuples(index=False, name=None)))
#print(usr)
cursor.executemany("INSERT INTO users (first_last_name) VALUES(?)", usr)

update = '''UPDATE users SET department = 'Genomics Core' WHERE first_last_name='Magali Michaut' '''
cursor.execute(update)
update = '''UPDATE users SET department = 'Genomics Core' WHERE first_last_name='Adrija Kalvisa' '''
cursor.execute(update)
for row in cursor.execute("SELECT * FROM users"):
    print(row)

## pipelines
# %%
pline = list(set(metadata[["pipeline"]].itertuples(index=False, name=None)))
cursor.executemany("INSERT INTO pipelines (name) VALUES(?)", pline)
for row in cursor.execute("SELECT * FROM pipelines"):
    print(row)

## assay

# %%
data = list(metadata.itertuples(index=False, name=None))
print(data)

#%%
cursor.executemany("""INSERT INTO assay (id, owner_id, created_at, codename, technology, sequencer_id, seq_kit_id, n_samples, is_paired, pipeline_id, processed_by_id, organism, organism_subgroup, origin, genomics_path, short_desc, long_desc, organism_version) \
                   VALUES(?, (SELECT user_id FROM users WHERE first_last_name=?),
                    ?, ?, ?, (SELECT seq_id FROM sequencers WHERE model = ?),
                      (SELECT seq_id FROM sequencing_kits WHERE kit = ?),
                        ?, ?, (SELECT pipeline_id FROM pipelines WHERE name = ?),
                          (SELECT user_id FROM users WHERE first_last_name=?),
                            ?, ?, ?, ?, ?, ?, ?)""", data)

#%%
for row in cursor.execute("SELECT * FROM assay"):
    print(row)
cursor = connection.execute('select * from assay')
cursor.description


## Close connection

# %%
connection.commit()
cursor.close()
connection.close()
