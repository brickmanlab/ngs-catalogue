import sqlite3

import pandas as pd


def read_db(database: str = "db/ngs_catalogue.db") -> pd.DataFrame:
    query = """
        SELECT
        a.*,
        u1.first_last_name AS owner,
        u2.first_last_name AS processed_by,
        s.model AS sequencer,
        k.kit AS seq_kit,
        p.pipeline_name AS pipeline
        FROM
        assay as a
        LEFT JOIN
        users AS u1 ON a.owner_id = u1.user_id
        LEFT JOIN
        users AS u2 ON a.processed_by_id = u2.user_id
        LEFT JOIN
        sequencers AS s ON a.sequencer_id = s.seq_id
        LEFT JOIN
        sequencing_kits AS k on a.seq_kit_id = k.seq_id
        LEFT JOIN
        pipelines AS p ON a.pipeline_id = p.pipeline_id;        
        """

    try:
        conn = sqlite3.connect(database)
        conn.execute("PRAGMA foreign_keys = ON")

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df
    except sqlite3.Error as er:
        raise er


def get_database():
    df = read_db()

    # debug
    # df.to_csv("db/db.csv", sep="\t", index=False)

    # remove foreign key columns and order by date ascending
    database = df[
        [
            "id",
            "assay",
            "owner",
            "created_on",
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
            "note",
            "genomics_path",
            "short_desc",
            "long_desc",
        ]
    ].copy()
    database["created_on"] = pd.to_datetime(database["created_on"], format="%Y%m%d")
    database["created_on"] = database["created_on"].dt.date

    database.sort_values("created_on", ascending=False, inplace=True)
    database.reset_index(drop=True, inplace=True)
    database.fillna("UNKNOWN", inplace=True)

    return database
