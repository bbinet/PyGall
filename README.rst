PyGall
======

About PyGall
------------

PyGall is a web photo gallery written in Python and built on the
`Pylons <http://pylonshq.com>`_ web framework.

PyGall is written by Bruno Binet and is licensed under a
BSD permissive license.

Features
--------

PyGall currently provides the following features:

* Upload photos either through the browser or manually on your webserver
  (scp, ftp, ...).

* Import photos in the gallery: they are automatically scaled and rotated
  using exif informations.
  If using `F-Spot <http://f-spot.org/>`_ as your personal photo management
  desktop application, PyGall can automatically import photos from F-Spot.

* Browse and view photos through a nice interface borrowed from
  `Galleria <http://galleria.aino.se/>`_.

Install
-------

You should have a working setuptools (or distribute) environment. I advise
you to use `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ to create
an isolated Python environment.

You can install PyGall with the following command::

    $ easy_install PyGall

PyGall is now installed. Let's create a configuration file for you PyGall
photo gallery::

    $ paster make-config PyGall pygall.ini

The newly created ``pygall.ini`` file will be used by Paster to initialize
the application, create the database, and serve your application.

So you need to create the database::

    $ paster setup-app pygall.ini#pygall

And finally, you can serve your PyGall application::

    $ paster serve pygall.ini

That's all, you can point your browser to http://127.0.0.1:5000 and start
using PyGall. You're ready to import your first photos!
