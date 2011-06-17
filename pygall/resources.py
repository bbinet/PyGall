from pyramid.security import Allow
from pyramid.security import Everyone, Authenticated

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'publicview'),
                (Allow, Authenticated, 'view'),
                (Allow, 'admin', 'edit')]
    def __init__(self, request):
        pass
