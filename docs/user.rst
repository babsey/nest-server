Introduction
==================
NEST Server is a server serving for the interaction between an application as a client
and the NEST Simulator.

Requirements for installing and starting nest-server
 * NEST Simulator (v2.18.0)


Installation
==================
To install NEST Server from python index package (pip):

.. code-block:: none

   pip3 install nest-server


Getting started
==================
To start NEST Server on the server:

.. code-block:: none

   nest-server start


Advanced
========

Options for nest-server (Defaults for host=127.0.0.1, port=5000)

.. code-block:: none

   nest-server <command> [-d] [-h <host>] [-p <port>] [-u <user>]

Showing usage for nest-server

.. code-block:: none

   nest-server

It stops NEST Desktop serving at defined address.

.. code-block:: none

   nest-server stop

It lists status of NEST Server serving at different addresses.

.. code-block:: none

   nest-server status

It prints the current version of NEST Server.

.. code-block:: none

   nest-server version
