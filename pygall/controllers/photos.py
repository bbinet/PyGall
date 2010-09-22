import logging
import os
from math import ceil
from webhelpers import paginate

from pylons import config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify

from pygall.lib.base import BaseController, render
from pygall.lib.imageprocessing import ImageProcessing
from pygall.lib.helpers import md5_for_file, unchroot_path, remove_empty_dirs
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class PhotosController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('photo', 'photos')

    # get safe and correct unchroot path

    def index(self, format='html'):
        """GET /photos: All items in the collection"""
        # url('photos')

    @jsonify
    def create(self):
        """POST /photos: Create a new item"""
        # url('photos')
        abspath, uri = unchroot_path(
            request.params.get('path', None),
            config['app_conf']['import_dir'])

        ip = ImageProcessing(
            config['app_conf']['import_dir'],
            os.path.join(
                config['pylons.paths']['static_files'],
                config['app_conf']['photos_public_dir']))

        error = False
        msg = None
        dest_uri = None
        try:
            # check same image has not already been imported
            f = open(abspath)
            try:
                hash = md5_for_file(f)
            finally:
                f.close()
            photo = Session.query(PyGallPhoto).filter_by(md5sum=hash)
            if photo.count() > 0:
                raise Exception("Same md5sum already exists in database")

            # process and import photos to public/data/photos dir
            date, dest_uri = ip.process_image(uri)

            # import image in db
            photo = PyGallPhoto()
            photo.uri = dest_uri
            photo.md5sum = hash
            photo.time = date
            Session.add(photo)
            Session.commit()

            remove_empty_dirs(config['app_conf']['import_dir'])
        except Exception, e:
            error = True
            msg = "%s [%s]" %(str(e), request.params.get('path', ''))
            log.error(msg)

        return {
            "status": not error,
            "msg": msg,
            "dest_uri": dest_uri
        }

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
        c.edit = bool(request.params.get('edit', False))
        return render('/pygall/photos/galleria.mako.html')
