import logging
from math import ceil
from webhelpers import paginate

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class PhotosController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('photo', 'photos')

    def index(self, format='html'):
        """GET /photos: All items in the collection"""
        # url('photos')

    def create(self):
        """POST /photos: Create a new item"""
        # url('photos')

    def new(self, format='html'):
        """GET /photos/new: Form to create a new item"""
        # url('new_photo')

    def update(self, id):
        """PUT /photos/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('photo', id=ID),
        #           method='put')
        # url('photo', id=ID)

    def delete(self, id):
        """DELETE /photos/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('photo', id=ID),
        #           method='delete')
        # url('photo', id=ID)

    def show(self, id, format='html'):
        """GET /photos/id: Show a specific item"""
        # url('photo', id=ID)

    def edit(self, id, format='html'):
        """GET /photos/id/edit: Form to edit an existing item"""
        # url('edit_photo', id=ID)

    @jsonify
    def editcomment(self):
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
