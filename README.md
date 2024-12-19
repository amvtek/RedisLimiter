# README

This project provides custom redis commands implemented in LUA that can be used for rate
limiting.

## Development setup

### Docker

For convenience a docker compose file is provided that provides:
* a dockerized redis server sufficient for test
* a devterm environment that allows running tests against the redis server

Prior to use docker compose, you shall run the provided `./setup` script to generate the
necessary configuration (`.env` file...)

To start the dockerized services, run this command in bash terminal :
```bash
$> docker compose up -d
```

To stop the dockerized services, run this command in bash terminal :
```bash
$> docker compose down
```

Once docker compose is running, to access the devterm developer console run this command
in bash terminal:
```bash
$> docker compose run --rm devterm bash
``` 

### Python tests

Tests for the custom redis commands are implemented in Python.

#### Virtual Environment creation
This step is not required if you are using docker compose

Run those commands in bash terminal :
```bash
$> cd path/to/project/git/folder # ...
$> python3 -m venv ../VENV
$> source ../VENV/bin/activate
(VENV)$> pip install -U pip setuptools wheel
(VENV)$> pip install -r requirements.txt
```

#### Running the tests

```bash
(VENV)$> python -m unittest -v
```
You may also install a fancy test runner like `pytest` ...
