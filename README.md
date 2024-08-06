# ngs-catalogue

## Development

### Local

```
module load miniconda/latest && source activate ngs_catalogue
bin/initdb.py

panel serve src/database_browser_v1.py --autoreload
```

### Docker

Build image

```bash
podman build . -t brickmanlab/ngs-catalogue:"$(git rev-parse --short HEAD)"
```

Run application

```bash
module load miniconda/latest && source activate ngs_catalogue
bin/initdb.py

podman run -d -p 5006:5006 -v ./db:/app/db brickmanlab/ngs-catalogue:"$(git rev-parse --short HEAD)"
```
