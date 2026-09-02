### How to execute pytest?

Important: The nest server should be started with these settings:

- it is unauthorized
- the exec call is enabled
- the Python code is not restricted
- and loaded modules are nest and numpy.

Run pytest

```
pytest
```

Run pytest in virtual environment.

```
uv run --env-file .env pytest
```

Run tests with NEST Server MPI is currently not implemented.
However you can run test of nest-clients for NEST Server MPI.

Start NEST Server MPI

```
mpirun -n 2 nest-server-mpi
```

Then run tests of NEST Server MPI in nest-clients (deselect `not_mpi` markers)

```
uv run pytest -v -m `not not_mpi`
```

### Debugging tests

Add debug logger.

```
import logging
logger = logging.getLogger()

...

logger.debug("Hello world")
```

Run pytest with debugs.

```
uv run --env-file .env pytest --log-level debug
```
