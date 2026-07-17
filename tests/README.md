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

Add debug log.
```
from app_test_client import logger

...

logger.debug("Hello world")
```

Run with log level for debug.
```
uv run --env-file .env --with pytest pytest --log-level debug
```
