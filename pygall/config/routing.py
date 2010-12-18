"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('/', controller='photos', action='galleria')
    map.connect('/edit', controller='photos', action='editcomment')
    map.connect('/{page:\d+}', controller='photos', action='galleria')
    map.resource('photo', 'photos')
    map.connect('/dates', controller='dates', action='index')
    map.connect('/tags', controller='tags', action='index')
    map.connect('/js/App.constants.js', controller='main', action='constants')

    # XXX: These URLs are hardcoded into pygall.lib.auth and
    # pygall.templates.pygall.account.login.mako.html.
    # These files are initialized before routing helper methods
    # (ie pylons.url) are available.
    map.connect('/account/login', controller='account', action='login')
    map.connect('/account/login_handler', controller='account', action='login_handler')
    map.connect('/account/logout', controller='account', action='logout')
    map.connect('/account/test_admin_access', controller='account', action='test_admin_access')
    map.connect('/account/test_user_access', controller='account', action='test_user_access')

    #map.connect('/{controller}/{action}')
    #map.connect('/{controller}/{action}/{id}')

    return map
