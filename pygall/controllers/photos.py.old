import logging
from math import ceil

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
from webhelpers import paginate

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class PhotosController(BaseController):

    @jsonify
    def edit(self):
        uri = request.params.getone('uri')
        comment = request.params.getone('comment')
        photo = Session.query(PyGallPhoto).filter_by(uri=uri).first()
        if not photo:
            abort(404)
        photo.description = comment
        Session.commit()
        return {
            'status': 0,
            'msg': 'OK'
        }


    def galleria(self, page=None):
        photo_q = Session.query(PyGallPhoto).order_by(PyGallPhoto.time.asc())
        if page is None:
            # default to last page
            page = int(ceil(float(photo_q.count()) / 33))
            redirect_to(controller='photos', action='galleria', page=page)

        c.photos = paginate.Page(photo_q, page=page, items_per_page=33)
        c.edit = request.params.get('edit')
        return render('galleria.mako.html')
