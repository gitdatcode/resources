# DATCODEdotCOM

This will be the repo for the DATCODE public website.

## Development Requirements

* Python3
* Neo4j

### Installation

* Create a virutal environment

```
python3 -m venv env
```

* Install the dependencies

```
pip install -r requirements.txt
```

### Run Tests

* Ensure that you have Neo4j installed with a database that has the password `datcoe_testing`
    * Run that database
* start the virutal environment

```
source env/bin/active
```

* Run all of the tests

```
python -m unittest discover datcode.test.api
```

* Target a specific test case

```
 python -m unittest datcode.test.api.controller.auth.test_login
```
