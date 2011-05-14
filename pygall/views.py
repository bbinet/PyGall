from pyramid.view import view_config
from pyramid.i18n import get_locale_name

from pygall.models import DBSession, MyModel

class Entry(object):
    def __init__(self, request):
        self.request = request
        self.debug = "debug" in request.params
        self.lang = get_locale_name(request)

    @view_config(route_name='home', renderer='index.html.mako')
    def home(self):
        dbsession = DBSession()
        model = dbsession.query(MyModel).filter(MyModel.name==u'root').first()
        return {
            'model': model,
            'lang': self.lang,
            'debug': self.debug
            }
