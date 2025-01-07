# README

This project provides custom redis commands implemented in LUA that can be used for rate
limiting.

## sliding_window command

This command implements a sliding window event counter which can be used  to enforce
rate limits. It allows checking several sliding window limits at once to enforce
efficient burst control.

It is available as a redis LUA script or as a LUA function exported by the
project LUA module.

Refers to provided [man page](docs/sliding_window.md) for details.

## Development 

### Developer machine setup

If you plan to use the provided Docker environment you must run the `./setup` script to
generate a `.env` file.

### Docker environment

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
The simplest way to run the tests is to use the dockerized devterm console.

In a bash terminal:
```bash
$> docker compose run --rm devterm bash
$> make tests
```

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
