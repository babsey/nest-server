### How to execute pytest?

Important: The nest server should be started with these settings:

- it is unauthorized
- the exec call is enabled
- the Python code is not restricted
- and loaded modules are nest and numpy.

#### Run pytest

Run pytest in virtual environment.

```
uv run --env-file .env.local pytest [-v]
```

#### Run pytest with NEST Server MPI

NOTE: Client tests with NEST Server MPI is currently not implemented.
However you can run client test of nest-client that send requests to NEST Server MPI.

Start NEST Server MPI

```
nest-server-mpi -n 2 start
```

Then run tests of [nest-client](https://github.com/nest/nest-client) (deselect `not_mpi` markers)

```
uv run pytest -m `not not_mpi`
```

### Debugging tests

Add debug logger.

```
import logging
logger = logging.getLogger()

...

logger.debug("Hello world")
```

Run pytest with debugging.

```
uv run --env-file .env.local pytest --log-level debug
```
