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
from pygall.security import groupfinder, init_security
from pygall.resources import init_resources
from pygall.lib.imageprocessing import ip
from pygall.lib.helpers import mkdir_p


def includeme(config):
    settings = config.registry.settings

    # add default values for some global settings
    templates_dir = list(filter(
        None, settings.get('templates_dir', '').splitlines()))
    templates_dir.append('pygall:templates')
    settings['mako.directories'] = templates_dir
    if 'photos_dir' not in settings:
        settings['photos_dir'] = 'photos'
    if 'upload_dir' not in settings:
        settings['upload_dir'] = 'upload'
    allow_cdn = asbool(settings.get('allow_cdn', 'false'))
    settings['allow_cdn'] = allow_cdn
    ip.set_dest_dir(settings['photos_dir'])
    mkdir_p(settings['upload_dir'])

    init_security(settings)
    init_resources(settings)

    authentication_policy = AuthTktAuthenticationPolicy(
            settings['authtkt_secret'], callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()

    config.add_settings(settings)
    config.set_root_factory(RootFactory)
    config.set_locale_negotiator(default_locale_negotiator)
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)

    # initialize database
    engine = sqlalchemy.engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)
    config.include(pyramid_tm.includeme)

    # formalchemy
    config.include('pyramid_formalchemy')
    config.include('fa.jquery')
    config.formalchemy_admin('admin', package='pygall',
            view='fa.jquery.pyramid.ModelView', factory=FAModelsFactory)

    # i18n
    config.add_translation_dirs('pygall:locale')

    # bind the mako renderer to other file extensions
    config.add_renderer('.mako', mako_renderer_factory)

    config.include(add_routes)
    config.include(add_views)

    config.scan('pygall')


def add_routes(config):
    # add routes to the entry view class
    config.add_route('photos_index', '/{page:\d*}')
    config.add_route('photos_new', '/photos/new')
    config.add_route('photos_create', '/photos/create')
    config.add_route('photos_delete', '/photos/delete')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

def add_views(config):
    # add the static views (for static resources)
    settings = config.registry.settings
    config.add_static_view('static', 'pygall:static')
    config.add_static_view('photos', settings['photos_dir'], permission='view')
    if 'static_dir' in settings:
        config.add_static_view('static_dir', settings['static_dir'],
                permission='view')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings)
    config.include(includeme)

    return config.make_wsgi_app()

