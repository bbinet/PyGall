from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from pyramid.settings import asbool
from pyramid_formalchemy.resources import Models

class RootFactory(object):
    __acl__ = [
            (Allow, 'admin', ALL_PERMISSIONS)]
    def __init__(self, request):
        self.request = request

def init_resources(settings):
    if asbool(settings.get('allow_anonymous', False)):
        RootFactory.__acl__.append((Allow, Everyone, 'view'))
    else:
        RootFactory.__acl__.append((Allow, Authenticated, 'view'))

class FAModelsFactory(Models):
    __acl__ = [(Allow, 'admin', ALL_PERMISSIONS)]
