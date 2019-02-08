- Install dependencies
  ```
  $ brew tap osgeo/osgeo4mac
  $ brew install postgres
  $ brew install postgis2 --build-from-source
  $ brew install grass7 --with-postgresql --with-libpq --with-matplotlib
  $ brew install gdal2 --with-postgresql --with-sfcgal --with-armadillo --with-qhull --with-opencl --with-libkml
  $ brew install gdal2-pdf --with-poppler
  $ brew install qgis3 --with-grass
  ```
- Install direnv as per https://direnv.net/
- Install pipenv as per https://github.com/pypa/pipenv
-
  ```sh
  $ cp envrc.example .envrc
  $ pipenv install
  $ ./bin/nyc_drinking_water ensure_postgis
  $ ./bin/nyc_drinking_water --help
  ```

- Copy TIGER data for NY and surrounding states using https://github.com/chinigo/tiger_tamer:
  ```sh
  $ ./bin/tame --projection 200100 all ./TIGER/2018
  ```
-
  ```sh
  $ ./bin/nyc_drinking_water run_all
  ```

# Results
![Rendered map of watersheds and pipelines](sample.jpeg?raw=true "Rendered map of watersheds and pipelines")
