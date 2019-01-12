- Install direnv as per https://direnv.net/
- Install pipenv as per https://github.com/pypa/pipenv
-
  ```sh
  $ brew install grass7
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
