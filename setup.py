try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='PyGall',
    version='0.3',
    description='Image gallery built with the Pylons web framework',
    author='Bruno Binet',
    author_email='binet.bruno@gmail.com',
    url='http://gitorious.org/PyGall',
    install_requires=[
        "Pylons>=0.9.7,<=0.9.99",
        "SQLAlchemy>=0.5,<=0.5.99",
        "gp.fileupload>=1.0,<=1.0.99",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'pygall': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'pygall': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    classifiers          = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Framework :: Pylons',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Multimedia :: Graphics :: Viewers',
        ],
    keywords='pylons wsgi image photo web gallery',
    license='BSD',
    entry_points="""
    [paste.app_factory]
    main = pygall.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
