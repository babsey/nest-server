FROM ubuntu:26.04
LABEL maintainer="Sebastian Spreizer <spreizer@web.de>"

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    curl ca-certificates \
    cmake ccache make gcc g++

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

ENV UV_PYTHON_CACHE_DIR=/root/.cache/uv/python

RUN uv venv /opt/venv
# Use the virtual environment automatically
ENV VIRTUAL_ENV=/opt/venv
# Place entry points in the environment at the front of the path
ENV PATH="/opt/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install nest-server==3.0.0b7

# NOTE: These lines can be removed for NEST Simulator 3.11 or up.
# Otherwise it will use build-in nest-server command from NEST Simulator.
RUN rm /opt/venv/bin/nest-server*
RUN uv pip install --reinstall --no-deps nest-server==3.0.0b7

# Health check: curl the endpoint every 30 seconds
# -f flag fails silently on HTTP errors (4xx, 5xx)
# exit 1 signals failure to Docker if curl fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:52425 || exit 1

ENV NEST_SERVER_HOST="0.0.0.0"
ENV NEST_SERVER_DISABLE_AUTH=1
ENV NEST_SERVER_DISABLE_RESTRICTION=1
ENV NEST_SERVER_ENABLE_EXEC_CALL=1
ENV NEST_SERVER_MODULES="import nest; import numpy; import numpy as np"

EXPOSE 52425
CMD ["uv", "run", "nest-server", "start"]
