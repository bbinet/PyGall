PyGall
======

About PyGall
------------

PyGall is a simple web photo gallery written in Python and built on the
`Pylons <http://pylonshq.com>`_ web framework.

PyGall is written by Bruno Binet and is licensed under a
BSD permissive license.

Code is hosted on github: https://github.com/inneos/PyGall.

Be warned that this image gallery is beta software, and not full featured.
It has been developped to fit my own needs, and may not suit your wishes.

But that being said, feel free to create a new issue to report bugs or ask for
new features at https://github.com/inneos/PyGall/issues.
Even better, since the code is hosted on github, feel free to fork and send
pull requests.

Features
--------

PyGall currently provides the following basic features:

* Upload photos through the browser. The photos are automatically scaled and
  rotated if needed.
  If using `F-Spot <http://f-spot.org/>`_ as your personal photo management
  desktop application, PyGall provides a script to automatically import photos
  from F-Spot.

* Browse and view photos through a nice interface borrowed from
  `Galleria <http://galleria.aino.se/>`_.

Install
-------

You should have a working setuptools (or distribute) environment. I advise
you to use `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ to create
an isolated Python environment.

Prior to actually install PyGall and its dependencies, you should install the
libjpeg and python development files, which are needed to compile the Python
Imaging Library dependency.
On Debian Linux you can do::

    $ sudo aptitude install build-essential libjpeg-dev python-dev

Then you can install PyGall with the following command::

    $ easy_install PyGall

PyGall is now installed. Let's generate a configuration file for your PyGall
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

