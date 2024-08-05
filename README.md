# ngs-catalogue

## Populate database

```bash
cd /maps/projects/dan1/data/Brickman/projects/ngs_catalogue/
module load miniconda/latest
source activate ngs_catalogue

#First remove current database version
rm db/ngs_catalogue.db

# Create empty database
sqlite3 db/ngs_catalogue.db < src/schema/database_v1.sql

# Populate database
python src/populate_database_v1.py
```


## Run app on DanGPU for testing
** Note**: This works only when ssh directly into dangpu (not on other computing nodes)

```bash
cd /maps/projects/dan1/data/Brickman/projects/ngs_catalogue/
module load miniconda/latest
source activate ngs_catalogue
panel serve src/database_browser_v1.py --autoreload
# locally
ssh -fNL localhost:5006:localhost:5006 USER@dangpu01fl.unicph.domain
```