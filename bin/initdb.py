#!/usr/bin/env python

import contextlib
import json
import logging
import sqlite3
import urllib.request
from pathlib import Path

import pandas as pd
import yaml

PROJECT_DIR = Path(__file__).parents[1]
DB_PATH = PROJECT_DIR / "db"
DB_FILE = DB_PATH / "ngs_catalogue.db"

DB_SCHEMA = PROJECT_DIR / "src" / "schema" / "v1.sql"
PROJECT_HOME = "/maps/projects/dan1/data/Brickman"
SCHEMA_V1 = "1.0"

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def backup() -> None:

    if DB_FILE.exists():
        logging.info("Backing up previous database")
        DB_FILE.rename(DB_FILE.with_suffix(".db.backup"))
    else:
        logging.info("No database was found ...")


def initialize() -> None:
    logging.info("Creating database tables")

    with contextlib.closing(sqlite3.connect(DB_FILE)) as db:
        with open(DB_SCHEMA, "r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_assays() -> pd.DataFrame:

    assays = {}
    metadata_files = (Path(PROJECT_HOME) / "assays/").glob("*/*.yml")

    logging.info("Loading assays ...")

    for meta_file in metadata_files:
        key = meta_file.parent.name
        content = yaml.safe_load(meta_file.read_bytes())
        if key in assays:
            assays[key].update(content)
        else:
            assays[key] = content

    return pd.DataFrame.from_dict(assays, orient="index")


def get_schema_columns(version: str):

    WHITELIST = ["__prompts__", "_extensions"]
    URL = "https://raw.githubusercontent.com/brickmanlab/ngs-template/master/assay/cookiecutter.json"
    res = urllib.request.urlopen(URL)
    if res.status != 200:
        raise ConnectionError("Provided URL for asssays metadata cannot be loaded")

    res_body = res.read()
    data = json.loads(res_body.decode("utf-8"))

    if data["__schema_version"] != version:
        raise ValueError(
            f"Provided schema version: {version} does not match! Found {data['__schema_version']}"
        )

    return sorted([x.replace("__", "") for x in data.keys() if x not in WHITELIST])


def populate() -> None:

    def get_(df: pd.DataFrame, column: str):
        if column in df.columns:
            return list(set(assays[[column]].itertuples(index=False, name=None)))

        raise ValueError(f"Column '{column}' not present in data!")

    assays = get_assays()
    schema_columns = get_schema_columns(version=SCHEMA_V1)

    logging.info("Validating schema ...")
    if sorted(assays.columns.tolist()) != schema_columns:
        raise ValueError(
            f"""
        Column names do not match!\n
        Expected: {sorted(schema_columns)}\n
        Given: {assays.columns.tolist()}
        """
        )

    # subset assays for columns in database
    db_columns = [
        "assay_id",
        "assay",
        "owner",
        "date",
        "eln_id",
        "technology",
        "sequencer",
        "seq_kit",
        "n_samples",
        "is_paired",
        "pipeline",
        "processed_by",
        "organism",
        "organism_version",
        "organism_subgroup",
        "origin",
        "short_desc",
        "long_desc",
        "note",
        "genomics_path",
    ]
    assays = assays[db_columns]

    with contextlib.closing(sqlite3.connect(DB_FILE)) as db:
        db.execute("PRAGMA foreign_keys = ON")

        with contextlib.closing(db.cursor()) as cursor:

            ## sequencing_kits
            cursor.executemany(
                "INSERT INTO sequencing_kits (kit) VALUES(?)", get_(assays, "seq_kit")
            )

            ## sequencers
            cursor.executemany(
                "INSERT INTO sequencers (model) VALUES(?)", get_(assays, "sequencer")
            )

            ## users
            cursor.executemany(
                "INSERT INTO users (first_last_name) VALUES(?)",
                get_(assays, "owner") + get_(assays, "processed_by"),
            )
            cursor.execute(
                """
                UPDATE users SET department = 'Genomics Core'
                WHERE first_last_name='Magali Michaut' OR first_last_name='Adrija Kalvisa'
                """
            )

            ## pipelines
            cursor.executemany(
                "INSERT INTO pipelines (pipeline_name) VALUES(?)",
                get_(assays, "pipeline"),
            )

            cursor.executemany(
                """
                INSERT INTO assay (
                    id, assay, owner_id, created_on, eln_id, technology, sequencer_id, seq_kit_id, 
                    n_samples, is_paired, pipeline_id, processed_by_id, organism, organism_version, 
                    organism_subgroup, origin, short_desc, long_desc, note, genomics_path)
                VALUES (
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
                list(assays.itertuples(index=False, name=None)),
            )

        db.commit()
        logging.info("DB population done ...")


def main():

    logging.info("Starting DB initialization ...")

    if not DB_PATH.exists():
        logging.info(f"Creating {DB_PATH}")
        DB_PATH.mkdir(exist_ok=True)
    else:
        backup()

    initialize()
    populate()


if __name__ == "__main__":
    main()
