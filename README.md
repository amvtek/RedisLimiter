# README

This project provides custom redis commands implemented in LUA that can be used for rate
limiting.

## Development setup

### Docker

For convenience a docker compose file is provided that allows running a redis server on
development machine. You can use another redis server than the one provided by the
project compose file.  

To start the dockerized redis server, run this command in bash terminal :
```bash
$> docker compose up -d
```

To stop the dockerized redis server, run this command in bash terminal :
```bash
$> docker compose down
```

### Python tests

Tests for the custom redis commands are implemented in Python.

#### Virtual Environment creation

Run those commands in bash terminal :
```bash
$> cd path/to/project/git/folder # ...
$> python3 -m venv ../VENV
$> source ../VENV/bin/activate
(VENV)$> pip install -U pip setuptools wheel
(VENV)$> pip install redis
```

#### Running the tests

```bash
(VENV)$> python -m unittest -v
```
You may also install a fancy test runner like `pytest` ...
