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

    # force some global settings
    settings['static_path'] = 'pygall:static'

    config = Configurator(root_factory=Root, settings=settings,
                          locale_negotiator=locale_negotiator)

    # initialize database
    engine = sqlalchemy.engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    config.include(pyramid_tm.includeme)

    # i18n
    config.add_subscriber('pygall.subscribers.add_renderer_globals',
            'pyramid.events.BeforeRender')
    config.add_subscriber('pygall.subscribers.add_localizer',
            'pyramid.events.NewRequest')
    config.add_translation_dirs('pygall:locale')

    # bind the mako renderer to other file extensions
    config.add_renderer('.mako', mako_renderer_factory)

    # add routes to the entry view class
    config.add_route('photos_index', '/')
    config.add_route('photos_new', '/photos/new')
    config.add_route('photos_create', '/photos/create')
    config.add_route('photos_editcomment', '/photos/editcomment')

    # we need to call scan() for the "home" routes
    config.scan()

    # add the static view (for static resources)
    config.add_static_view('static', settings['static_path'])

    return config.make_wsgi_app()

