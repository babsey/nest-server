Development
===========
NEST Server is a Python server serving for the interaction between the client
and the NEST Simulator.


Requirements for nest-server
 * Python 3.4 or higher
 * NEST Simulator (v2.18.0)


Development environment
-----------------------

Build singularity image containing requirements (NEST, Python packages) for developing NEST Server.

.. code-block:: none

   singularity build nest-server-dev.sif nest-desktop/singularity/nest-server-dev.def

Run singularity container

.. code-block:: none

   singularity shell nest-server-dev.sif


Setup
-----
Clone NEST Server from the github:

.. code-block:: none

   git clone https://github.com/babsey/nest-server

Install NEST Server from source code using :code:`pip` (where it finds :code:`setup.py`).
Best option is to install it in user home using :code:`pip install --user`.

.. code-block:: none

   pip3 install --user --no-deps -e nest-server


Getting started
---------------
You can read `Getting started` in User Documentation to start NEST Server.
Starting NEST Server :code:`nest-server start` equivalent to the command:

.. code-block:: none

   uwsgi --module nest_server.main:app --http-socket <host>:<port> --uid <user> --daemonize "/tmp/nest-server-<host>-<port>.log"


To start uwsgi with local files:

.. code-block:: none

   uwsgi --module nest_server.main:app --http-socket :5000


Python Package Index (PyPI)
---------------------------
The Python Package Index **nest-server** includes an executive command :code:`nest-server` and a Python library :code:`nest_server`.

First, update the version of nest-server in :code:`nest_server/__init__.py`.

Next, remove the folders:

.. code-block:: none

   rm -rf build/ dist/ nest_server.egg-info/

Then generate distribution packages of `nest-server` for PyPI:

.. code-block:: none

   python3 setup.py sdist bdist_wheel

Finally, upload `nest-server` to PyPI:

.. code-block:: none

   python3 -m twine upload dist/*


Sphinx documentation
--------------------
To install sphinx and readthedocs theme via  :code:`pip`:

.. code-block:: none

   pip3 install sphinx sphinx_rtd_theme


To build sphinx documentation to  :code:`_build` folder:

.. code-block:: none

   make html


Readthedocs webpage
-------------------
It automatically builds docs for master when pulling commits to master.
Docs for latest and stable depends on their github tags.



Scripts
-------
- A script for simulation.
- A script for building models.


RESTful API
-----------
The RESTful API of NEST Server is defined to forward the request to the function of the module directly.

A schematic of the GET request would looked like it:

.. code-block:: none

   curl <host>:<port>/api/<module>/<function>?arg1=value1&arg2=value2


A schematic of the POST request:

.. code-block:: none

   curl -d "arg1=value1&arg2=value2" <host>:<port>/api/<module>/<function>


A schematic of the JSON request:

.. code-block:: none

   curl -H "Content-Type: application/json" -d '{"arg1": "value1", "arg2": "value2"}' <host>:<port>/api/<module>/<function>
