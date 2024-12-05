import contextlib
import sqlite3

import pandas as pd
import panel as pn

DB_FILE = "db/ngs_catalogue.db"


# connect to the database and fetch data
def fetch_data(query, db):
    with contextlib.closing(sqlite3.connect(db)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        # read query result into pandas dataframe
        df = pd.read_sql_query(query, connection)

    return df


query = """
        SELECT
        a.*,
        u1.first_last_name AS owner,
        u2.first_last_name AS processed_by,
        s.model AS sequencer,
        k.kit AS seq_kit,
        p.pipeline_name AS pipeline
        FROM assay as a
        LEFT JOIN users AS u1 ON a.owner_id = u1.user_id
        LEFT JOIN users AS u2 ON a.processed_by_id = u2.user_id
        LEFT JOIN sequencers AS s ON a.sequencer_id = s.seq_id
        LEFT JOIN sequencing_kits AS k on a.seq_kit_id = k.seq_id
        LEFT JOIN pipelines AS p ON a.pipeline_id = p.pipeline_id;        
        """

df = fetch_data(query, DB_FILE)


# remove foreign key columns, order, and sort by date descending
def process_data(df):
    df = df.loc[
        :,
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
        ],
    ]

    df["created_on"] = pd.to_datetime(df["created_on"], format="%Y%m%d")
    df = (
        df.sort_values("created_on", ascending=False)
        .reset_index(drop=True)
        .fillna("UNKNOWN")
    )

    return df


df = process_data(df)


# Define widgets
pn.extension("tabulator", inline=True)
pn.extension(sizing_mode="stretch_width")


# note: visible fields: id, assay, owner, created_on, organism,short_desc
df_widget = pn.widgets.Tabulator(
    df,
    disabled=True,
    selectable=True,
    hidden_columns=[
        "index",
        "assay",
        "eln_id",
        "technology",
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
        "long_desc",
    ],
)
df_widget


# Selection widgets


def multiselector(table, columns):
    widgets = {}
    for column in columns:
        widget = pn.widgets.MultiSelect(
            name=column, options=sorted(list(df[column].unique())), margin=(0, 20, 0, 0)
        )
        widgets[column] = widget
    return widgets


widgets = multiselector(df_widget, ["owner", "assay"])

# print(list(widgets.keys()))
# print(list(widgets.values()))

pn.template.FastListTemplate(
    site="Brickman Lab",
    title="NGS Catalogue",
    accent="#4051B5",
    main=[
        pn.Row(*widgets.values(), height=100),
        pn.Row(df_widget, height=650, scroll=False),
    ],
    main_max_width="1500px",
).servable()

# own = pn.widgets.MultiSelect(
#     name="owner", options=sorted(list(df.owner.unique())), margin=(0, 20, 0, 0)
# )
# df_widget.add_filter(own, "owner")


# asy = pn.widgets.MultiSelect(
#     name="assay", options=sorted(list(df.assay.unique())), margin=(0, 20, 0, 0)
# )
# df_widget.add_filter(asy, "assay")


# org = pn.widgets.MultiSelect(
#     name="organism", options=sorted(list(df.organism.unique())), margin=(0, 20, 0, 0),
# )
# df_widget.add_filter(org, "organism")


# def contains_filter(df, pattern, column):
#     if desc.value:
#         return df[df[column].str.contains(pattern, case=False, na=False)]
#     else:
#         return df

# desc = pn.widgets.TextInput(name="short_desc", placeholder="Enter key word...")
# df_widget.add_filter(pn.bind(contains_filter, pattern=desc, column="short_desc"))


# # show all metadata for dataset on row click

# def show_row_info(event):
#     # print(f'Clicked cell in column {event.column}, row {event.row}')

#     index = event.row
#     data = df.loc[index, :]

#     meta = "**Assay Details**\n\n"
#     for column, value in data.items():
#         meta += f"**{column}:** {value}\n\n"

#     meta_placeholder.object = meta

#     return meta_placeholder

# meta_placeholder = pn.pane.Markdown("Click a record to see metadata here")
# df_widget.on_click(show_row_info)


# # populate layout template

# df_column = pn.Column(df_widget, width=1150, scroll=True)
# meta_column = pn.Column(meta_placeholder, width=310, scroll=True)

# pn.template.FastListTemplate(
#     site="Brickman Lab",
#     title="NGS Catalogue",
#     accent="#4051B5",
#     main=[
#         pn.Row(own, asy, org, desc, height=100),
#         pn.Row(df_column, meta_column, height=650, scroll=False),
#     ],
#     main_max_width="1500px",
# ).servable()
