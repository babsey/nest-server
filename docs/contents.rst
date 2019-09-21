Introduction
==================
NEST Server is a Python server serving for the interaction between the client
and the NEST Simulator.


Requirements for installing and starting nest-server
 * Python 3.4 or higher
 * NEST Simulator (v2.18.0)


Installation
==================
To install NEST Server from python index package (pip):

.. code-block:: none

   pip3 install nest-server


With this command these requirements are also installed:
 * Numpy
 * Flask
 * Flask-cors
 * NESTML


Getting started
==================
To start NEST Server on the server:

.. code-block:: none

   nest-server start



Scripts
==================
- A script for simulation.
- A script for building models.


RESTful API
==================
The RESTful API of NEST Server is defined to forward the request to the function of the module directly.

A schematic of the GET request would looked like it:

.. code-block:: none

   curl <host>:<port>/api/<module>/<function>?arg1=value1&arg2=value2


A schematic of the POST request:

.. code-block:: none

   curl -d "arg1=value1&arg2=value2" \
      <host>:<port>/api/<module>/<function>


A schematic of the JSON request:

.. code-block:: none

   curl -H "Content-Type: application/json" \
      -d '{"arg1": "value1", "arg2": "value2"}' \
      <host>:<port>/api/<module>/<function>
