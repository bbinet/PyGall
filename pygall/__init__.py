from pyramid.config import Configurator
from pyramid.mako_templating import renderer_factory as mako_renderer_factory
import sqlalchemy
import sqlahelper
import pyramid_tm

from pygall.resources import Root

def locale_negotiator(request):
    """ Our locale negotiator. Returns a locale name or None.
    """
    return request.params.get('lang')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = Configurator(root_factory=Root, settings=settings,
                          locale_negotiator=locale_negotiator)

    # initialize database
    engine = sqlalchemy.engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    config.include(pyramid_tm.includeme)

    # bind the mako renderer to other file extensions
    config.add_renderer('.mako.html', mako_renderer_factory)
    config.add_renderer('.mako.js', mako_renderer_factory)

    # add routes to the entry view class
    config.add_route('home', '/')

    # we need to call scan() for the "home" routes
    config.scan()

    # add the static view (for static resources)
    config.add_static_view('static', 'pygall:static')

    return config.make_wsgi_app()

