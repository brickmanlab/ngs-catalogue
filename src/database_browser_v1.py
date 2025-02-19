import panel as pn

from utils import get_database

# Define widgets
pn.extension(inline=True)
pn.extension("tabulator")
pn.extension(sizing_mode="sizing_mode")

DATABASE = get_database()


def clear_filter(event):
    global owner, assay, organism, origin
    owner.value = []
    assay.value = []
    organism.value = []
    origin.value = []


def contains_filter(df, pattern, column):
    if not pattern:
        return df

    return df[df[column].str.contains(pattern, case=False, na=False)]


def close_meta(event):
    global meta_placeholder

    meta_clone_btn.__setattr__("visible", False)
    meta_placeholder.__setattr__("visible", False)


def show_row_info(event):
    global DATABASE

    # print(f'Clicked cell in column {event.column}, row {event.row}')
    index = event.row
    data = DATABASE.loc[index, :]

    simlink = f"ln -s /maps/projects/dan1/data/Brickman/assays/{data['id']} /maps/projects/dan1/data/Brickman/projects/<PROJECT_ID>/data/assays/"
    labguru_link = f"https://sund.labguru.com/knowledge/projects/{data['eln_id']}"

    meta = f"""
    ## {data["id"]}<br><button type="button" onclick="navigator.clipboard.writeText('{simlink}')">Copy link to assay</button>
    NGS: {data["technology"]} <br>
    Performed by **{data["owner"]}** on {data["created_on"]}<br>
    Labguru id: [{data["eln_id"]}]({labguru_link})<br>
    Origin: {data["origin"]}<br>

    ### Samples
    Num. of sampels: {data["n_samples"]}<br>
    Organism: {data["organism"]}<br>
    Organism subgroup: {data["organism_subgroup"]}<br>
    Note: {data["note"]}

    ### Sequencing details
    Sequencer: {data["sequencer"]}<br>
    Kit: {data["seq_kit"]}<br>
    Read setup: {data["is_paired"]}<br>
    
    ### Preprocessing
    User: {data["processed_by"]}<br>
    Genome: {data["organism_version"]}<br>
    Pipeline: {data["pipeline"]}<br>
    Raw reads: {data["genomics_path"]}

    ### Description
    {data["short_desc"]}

    {data["long_desc"]}
    """

    meta_placeholder.object = meta
    meta_clone_btn.__setattr__("visible", True)
    meta_placeholder.__setattr__("visible", True)


####################################################################################################
# NAVBAR


# note: visible fields: id, assay, owner, created_on, organism,short_desc
tabulator = pn.widgets.Tabulator(
    DATABASE,
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

# Selection widgets
owner = pn.widgets.MultiSelect(
    name="Owner (responsible person)",
    options=sorted(list(DATABASE.owner.unique())),
    size=5,
)

assay = pn.widgets.MultiSelect(
    name="Assay (NGS technology)",
    options=sorted(list(DATABASE.assay.unique())),
    size=5,
)

organism = pn.widgets.MultiSelect(
    name="Organism",
    options=sorted(list(DATABASE.organism.unique())),
    size=5,
)

origin = pn.widgets.MultiSelect(
    name="Internal/External",
    options=sorted(list(DATABASE.origin.unique())),
)

description = pn.widgets.TextInput(
    name="Short description", placeholder="Enter key word..."
)

clear_btn = pn.widgets.Button(
    name="Clear filters", button_type="primary", sizing_mode="stretch_width"
)
clear_btn.on_click(clear_filter)

# show all metadata for dataset on row click
meta_clone_btn = pn.widgets.Button(name="X", button_type="primary", visible=False)
meta_clone_btn.on_click(close_meta)

meta_placeholder = pn.pane.Markdown(
    "Click a record to see metadata here", width=450, visible=False
)

# Filters and events
tabulator.add_filter(owner, "owner")
tabulator.add_filter(assay, "assay")
tabulator.add_filter(organism, "organism")
tabulator.add_filter(origin, "origin")
tabulator.add_filter(pn.bind(contains_filter, pattern=description, column="short_desc"))

tabulator.on_click(show_row_info)

####################################################################################################
# BODY LAYOUT

pn.template.FastListTemplate(
    site="Brickman Lab",
    title="NGS Catalogue",
    accent="#4051B5",
    main=[
        pn.Row(
            pn.Column(owner),
            pn.Column(assay),
            pn.Column(organism),
            pn.Column(origin),
            pn.Column(description, clear_btn),
        ),
        pn.Row(
            pn.Column(tabulator, scroll=True, sizing_mode="stretch_width"),
            pn.Column(
                pn.Row(meta_clone_btn),
                pn.Row(meta_placeholder),
                scroll=True,
            ),
        ),
    ],
    raw_css=["div.card-margin:nth-child(2) { max-height: 750px; }"],
).servable()

