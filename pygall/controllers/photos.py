import logging
from math import ceil

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from webhelpers import paginate

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class PhotosController(BaseController):

    def index(self, format='html'):
        photo_q = Session.query(PyGallPhoto).order_by(PyGallPhoto.time.asc())
        return render('index.mako.html')

    def show(self, id, format='html'):
        photo_q = Session.query(PyGallPhoto).get(id)
        return render('show.mako.html')

    def galleria(self, page=None):
        photo_q = Session.query(PyGallPhoto).order_by(PyGallPhoto.time.asc())
        if page is None:
            # default to last page
            page = int(ceil(float(photo_q.count()) / 33))
            redirect_to(controller='photos', action='galleria', page=page)

        c.photos = paginate.Page(photo_q, page=page, items_per_page=33)
        return render('galleria.mako.html')
