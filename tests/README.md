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
uv run --env-file .env --with pytest pytest
```

### Debugging tests

Get Logger from logging
```
import logging
logger = logging.getLogger()
```

Add debug breakpoint.
```
logger.debug("Hello world")
```

Run with log level for debug.
```
uv run --env-file .env --with pytest pytest --log-level debug
```
