"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('/', controller='photos', action='galleria')
    map.connect('/edit', controller='photos', action='editcomment')
    map.connect('/{page:\d+}', controller='photos', action='galleria')
    map.resource('photo', 'photos')
    map.connect('/import/new', controller='import', action='new')
    map.connect('/import/upload', controller='import', action='upload')
    map.connect('/import/delete', controller='import', action='delete')
    map.connect('/import', controller='import', action='index')
    map.connect('/dates', controller='dates', action='index')
    map.connect('/tags', controller='tags', action='index')
    map.connect('/js/App.constants.js', controller='main', action='constants')

    #map.connect('/{controller}/{action}')
    #map.connect('/{controller}/{action}/{id}')

    return map
