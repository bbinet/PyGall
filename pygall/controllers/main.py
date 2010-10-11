import logging

from pylons import request, response, session, tmpl_context as c

from pygall.lib.base import BaseController, render

log = logging.getLogger(__name__)

class MainController(BaseController):

    def constants(self):
        # render the javascript constants
        return render('/pygall/main/constants.mako.js')
