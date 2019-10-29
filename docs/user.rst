Usage
=====
NEST Server is a server serving for the interaction between an application as a client
and the NEST Simulator.

Requirements for installing and starting nest-server
 * NEST Simulator (v2.18.0)


Installation
------------
To install NEST Server from python index package (pip):

.. code-block:: bash

   pip3 install nest-server


Getting started
---------------
To start NEST Server on the server:

.. code-block:: bash

   nest-server start


Advanced
--------

Options for nest-server (Defaults for host=127.0.0.1, port=5000)

.. code-block:: bash

   nest-server <command> [-d] [-h <host>] [-p <port>] [-u <user>]

Showing usage for nest-server

.. code-block:: bash

   nest-server

Start NEST Server serving at default address.

.. code-block:: bash

   nest-server start

Stop NEST Server serving at default address.

.. code-block:: bash

   nest-server stop

List status of NEST Server serving at different addresses.

.. code-block:: bash

   nest-server status

Print the current version of NEST Server.

.. code-block:: bash

   nest-server version

Monitor the requests of NEST Server.

.. code-block:: bash

   nest-server log
