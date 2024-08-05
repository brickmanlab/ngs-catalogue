import pandas as pd
import sqlite3
import panel as pn

# connect to the database
connection = sqlite3.connect("db/ngs_catalogue.db")
connection.execute("PRAGMA foreign_keys = ON")

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

# read query result into pandas dataframe
df = pd.read_sql_query(query, connection)

# close database connection
connection.close()

df.to_csv('db/db.csv', sep='\t', index=False)

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
        "long_desc"        
    ]
]
database["created_on"] = pd.to_datetime(database["created_on"], format="%Y%m%d")
database["created_on"] = database["created_on"].dt.date
database = database.sort_values("created_on", ascending=False)

# print(database.isnull().any())
database.fillna("UNKNOWN", inplace=True)

# database.to_csv('db/database.csv', sep='\t', index=False)


# Serve panel database

# define widgets

pn.extension(sizing_mode="stretch_width")

# note: visible fields: id, owner,created_on,technology,organism,short_desc
df_widget = pn.widgets.Tabulator(
    database,
    disabled=True,
    selectable=True,
    hidden_columns=[
        "index",
        "assay",
        "eln_id",
        "sequencer",
        "seq_kit",
        "n_samples",
        "is_paired",
        "pipeline",
        "processed_by",
        "organism_version",
        "organism_subgroup",
        "origin",
        "note",
        "genomics_path",
        "long_desc"        
    ],
)
df_widget

own = pn.widgets.MultiSelect(
    name="owner", options=list(database.owner.unique()), margin=(0, 20, 0, 0)
)
df_widget.add_filter(own, "owner")

org = pn.widgets.MultiSelect(
    name="organism", options=list(database.organism.unique()), margin=(0, 20, 0, 0)
)
df_widget.add_filter(org, "organism")

desc = pn.widgets.TextInput(name="short_desc", placeholder="Enter key word...")


def contains_filter(database, pattern, column):
    if desc.value:
        return database[database[column].str.contains(pattern)]
    else:
        return database


df_widget.add_filter(pn.bind(contains_filter, pattern=desc, column="short_desc"))


# show all metadata for dataset on row click
def show_row_info(event):
    print(f'Clicked cell in column {event.column}, row {event.row}')
    index = event.row
    data = database.loc[index, :]

    meta = "**Assay Details**\n\n"
    for column, value in data.items():
        meta += f"**{column}:** {value}\n\n"

    pn.panel(pn.pane.Markdown(meta)).show()


df_widget.on_click(show_row_info)


# populate layout template
pn.template.FastListTemplate(
    site="Brickman Lab",
    title="NGS Catalogue",
    accent="#4051B5",
    main=[
        pn.Row(own, org, desc, height=150),
        #pn.Row(own, org, height=150),
        pn.Row(df_widget, height=600, scroll=True),
    ],
    main_max_width="1500px",
).servable()
