import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from webhelpers import paginate

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class PhotosController(BaseController):

    def index(self, page=1):
        photo_q = Session.query(PyGallPhoto).order_by(PyGallPhoto.time.desc())
        c.photos = paginate.Page(photo_q, page=page, items_per_page=33)
        return render('galleria.mako.html')
