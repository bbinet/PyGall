PyGall
======

About PyGall
------------

PyGall is a simple web photo gallery written in Python and built on the
`Pyramid <http://docs.pylonsproject.org/docs/pyramid.html>`_ web framework.

PyGall is licensed under a BSD permissive license.

Code is hosted on github: https://github.com/inneos/PyGall.

Be warned that this image gallery is beta software, and not full featured.
It has been developped to fit my own needs, and may not suit your wishes.

But that being said, feel free to report bugs or ask for new features at
https://github.com/inneos/PyGall/issues.
Even better, since the code is hosted on github, feel free to fork and send
pull requests.

Features
--------

PyGall currently provides the following features:

* Browse and view photos through a nice interface borrowed from
  `Galleria <http://galleria.aino.se/>`_.

* Bulk upload of photos through the browser using `jQuery-File-Upload
  <https://github.com/blueimp/jQuery-File-Upload>`_. The photos are
  automatically scaled and rotated if needed.

* If using `F-Spot <http://f-spot.org/>`_ as your personal photo management
  desktop application, PyGall provides a script to automatically import photos
  from F-Spot and keep in sync your PyGall gallery.

* Administer your PyGall gallery via a dedicated interface that let you update
  photo metadata such as date, rating, or description. You can also delete
  photos, or organize them through tags (which will soon be used to provide
  different views in PyGall).

* Allow templates override so that the user interface can be easily customized
  to your needs.

For upcoming features, you can have a look at
https://github.com/inneos/PyGall/blob/master/TODO.txt

Install
-------

Prior to actually install PyGall and its dependencies, you should install the
libjpeg and python development files, which are needed to compile the Python
Imaging Library dependency.
On Debian Linux you can do::

    $ sudo aptitude install build-essential libjpeg-dev python-dev

You should have a working setuptools (or distribute) environment. I advise
you to use `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ to create
an isolated Python environment.
On Linux you can do::

    $ wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py 
    $ python virtualenv.py --no-site-packages venv

This will create a virtual environment named `venv` that we'll use to install
PyGall. See http://www.virtualenv.org for more information on virtualenv.

So let's install PyGall in the freshly created venv::

    $ venv/bin/pip install PyGall

PyGall is now installed. We need to make a configuration file for your
PyGall photo gallery. The easiest way is to copy the file from the PyGall
repository and customize it to your needs::

    $ wget https://raw.github.com/inneos/PyGall/master/production.ini

First, you should edit ``production.ini`` and set a unique random value for
the ``authtkt_secret`` (instead of the `̀ changeme`` default value) to guard
against the theft of authentication session.

This ``production.ini`` file will be used by Paster to initialize the
application, create the database, and serve your application.

So you need to setup PyGall, generate a configuration for
authentication (auth.cfg) and create the database (PyGall.db)::

    $ venv/bin/python -m pygall.scripts.setup production.ini

And finally, you can serve your PyGall application::

    $ venv/bin/paster serve production.ini

That's all, you can point your browser to http://127.0.0.1:6543 and start
using PyGall.

By default, the following 2 user accounts are set up:

An administrator account
  | login: admin
  | password: admin

A guest account
  | login: guest
  | password: guest

.. note::

    You can edit these users by editing the auth.cfg file located in the same
    directory as your production.ini file. Note that password hashes are
    generated using the htpasswd utility. For example, to add a user named
    "john", you will generate his password hash with::

        $ htpasswd -n john

    Then you just have to append a new line to the file auth.cfg copying the
    output of the previous htpasswd command.

    If john should be in group admin, then just append ":admin" to the line.

    Also remember to change the passwords of the default accounts (or remove
    these default accounts entirely).

Log in as administrator and you're ready to import your first photos!

Use PyGall
----------

By default, when anonymous, you will be prompted for login: only registered
users will be allowed to view the gallery.

If you want to allow any anonymous user to view the gallery, you can set
`allow_anonymous = true` in the `production.ini` config file.

Once logged in, you will be redirected to the PyGall gallery index page.
Then if you are part of the admin group, you will be allowed both to upload new
photos and to edit, delete existing photos. For that purpose, you can go
through the 'Upload' and 'Admin' link in the upper right corner of the gallery.

If you are using F-spot as your personnal photo management desktop application,
you can rather choose to use the F-spot synchronization script provided with
PyGall to import photos coming from F-spot directly in your gallery.
To use it, simply run the following command::

   $ venv/bin/python -m pygall.scripts.fspot_sync --fspot-photosdir=/path/to/fspot/photos production.ini

By default, all photos that have the tag 'pygall' will be imported in your
gallery. Pass `--help` option to see all possible options::

   $ venv/bin/python -m pygall.scripts.fspot_sync --help

If you want to share your gallery to other people, please refer to the
previous note to create new user accounts.

Note that PyGall has been internationalized, and is available in both french
and english languages. To change the current locale, you can set the `_LOCALE_`
parameter in the query string of the current url. So the url would look like::

    http://127.0.0.1:6543/?_LOCALE_=en

or::

    http://127.0.0.1:6543/?_LOCALE_=fr

Customize look and feel
-----------------------

You can easily customize the look and feel of the PyGall gallery by overriding
some mako templates and providing your own static resources (css, images).

To override some default PyGall templates, you have to update your
`production.ini` and uncomment the line::

    templates_dir = %(here)s/custom_templates

Then create the `custom_templates` directory, and put some mako templates in
there. For example, you can copy the default PyGall templates from
https://github.com/inneos/PyGall/tree/master/pygall/templates and update them
as needed.

If you want to include some static resources, you can also activate a new
static view by uncommenting the line::

    static_dir = %(here)s/custom_static

Then create the `custom_static` directory, and put some static files in there.
You can now access these static resources from your mako templates with
something like::

    ${request.static_url(request.registry.settings['static_dir'] + /path/to/resource')}

Extend PyGall
-------------

If the customization of the look and feel is not enough, you can go further and
create a new Pyramid application which extends PyGall.

Thus you can use all the flexibility of the Pyramid web framework to make your
own application and use PyGall views internally.

Please refer to the `Pyramid web framework documentation
<https://docs.pylonsproject.org/docs/pyramid.html>`_ to know more about
application customization.

