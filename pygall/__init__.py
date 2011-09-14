from pyramid.config import Configurator
from pyramid.mako_templating import renderer_factory as mako_renderer_factory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.i18n import default_locale_negotiator
from pyramid.settings import asbool
import sqlalchemy
import sqlahelper
import pyramid_tm

from pygall.resources import RootFactory, FAModelsFactory
from pygall.security import groupfinder
from pygall.lib.imageprocessing import ip
from pygall.lib.helpers import mkdir_p


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # force some global settings
    settings['static_path'] = 'pygall:static'
    settings['mako.directories'] = ['pygall:templates']
    allow_cdn = asbool(settings.get('allow_cdn', 'false'))
    settings['allow_cdn'] = allow_cdn
    ip.set_dest_dir(settings['photos_dir'])
    mkdir_p(settings['upload_dir'])

    authentication_policy = AuthTktAuthenticationPolicy(
            settings['authtkt_secret'], callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=RootFactory, settings=settings,
                          locale_negotiator=default_locale_negotiator,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy)

    # initialize database
    engine = sqlalchemy.engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    config.include(pyramid_tm.includeme)

    # formaclhemy
    config.include('pyramid_formalchemy')
    config.include('fa.jquery')
    config.formalchemy_admin('admin', package='pygall',
            view='fa.jquery.pyramid.ModelView', factory=FAModelsFactory)

    # i18n
    config.add_translation_dirs('pygall:locale')

    # bind the mako renderer to other file extensions
    config.add_renderer('.mako', mako_renderer_factory)

    # add routes to the entry view class
    config.add_route('photos_index', '/{page:\d*}')
    config.add_route('photos_new', '/photos/new')
    config.add_route('photos_create', '/photos/create')
    config.add_route('photos_delete', '/photos/delete')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    # we need to call scan() for the "home" routes
    config.scan()

    # add the static views (for static resources)
    config.add_static_view('static', settings['static_path'])
    config.add_static_view('photos', settings['photos_dir'], permission='view')

    return config.make_wsgi_app()

