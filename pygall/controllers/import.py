import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from pygall.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ImportController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/import.mako')
        # or, return a response
        return 'Hello World'
