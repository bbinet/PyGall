from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from pyramid_formalchemy.resources import Models

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'publicview'),
                (Allow, Authenticated, 'view'),
                (Allow, 'admin', ALL_PERMISSIONS)]
    def __init__(self, request):
        self.request = request

class FAModelsFactory(Models):
    __acl__ = [(Allow, 'admin', ALL_PERMISSIONS)]
