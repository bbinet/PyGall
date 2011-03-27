import logging
import os
from math import ceil
from tempfile import mkdtemp
from shutil import rmtree

from pylons import url, config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector
from webhelpers import paginate

from pygall.lib.base import BaseController, render
from pygall.lib.imageprocessing import ImageProcessing
from pygall.lib.archivefile import extractall
from pygall.lib.helpers import md5_for_file, unchroot_path, remove_empty_dirs
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

ip = ImageProcessing(os.path.join(
        config['pylons.paths']['static_files'],
        config['app_conf']['photos_public_dir']))

class PhotosController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('photo', 'photos')

    # get safe and correct unchroot path

    def index(self, format='html'):
        """GET /photos: All items in the collection"""
        # url('photos')
        log.debug('index')
        return 'index'

    @ActionProtector(has_permission('admin'))
    @jsonify
    def create(self):
        """POST /photos: Create a new item"""
        # url('photos')
        log.debug('create')

        # gp.fileupload stores uploaded filename in fieldstorage
        fieldstorage = request.params.get('file', u'')
        if fieldstorage == u'':
            log.debug("Nothing uploaded")
            abort(400)
        filepath = os.path.join(
            config['global_conf']['upload_dir'],
            fieldstorage.file.read().strip(" \n\r"))
        log.debug("File has been downloaded to %s" %(filepath))
        fieldstorage.file.close()

        # extract to a tmpdir that we should delete immediately
        # after import is done.
        tmpdir = mkdtemp(dir=config['upload_dir'])

        try:
            extractall(filepath, tmpdir)
            # delete the uploaded archive once extracted
            os.remove(filepath)

            # walk in import directory to import all image files
            for dirpath, dirs, files in os.walk(tmpdir, topdown=False):
                for filename in files:
                    abspath = os.path.join(dirpath, filename)
                    log.debug("Importing image: %s" %abspath)
                    try:
                        self._import(abspath)
                    except Exception as e:
                        # TODO: log error in session (flash message)
                        log.error("Error while importing image, skip" \
                                "file: %s\nException: %s" %(abspath, str(e)))
        except Exception, e:
            # TODO: log error in session (flash message)
            raise e
        finally:
            rmtree(tmpdir)

        return { 'success': True }


    def _import(self, abspath):
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
        try:
            date, dest_uri = ip.process_image(abspath)
        except Exception as e:
            ip.remove_image(abspath)
            raise e

        # import image in db
        photo = PyGallPhoto()
        photo.uri = dest_uri
        photo.md5sum = hash
        photo.time = date
        Session.add(photo)
        Session.commit()


    @ActionProtector(has_permission('admin'))
    def new(self, format='html'):
        """GET /photos/new: Form to create a new item"""
        # url('new_photo')
        return render('/pygall/photos/new.mako.html')

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

    @ActionProtector(has_permission('admin'))
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


    # The photos gallery itself is publicly available.
    # Add an ActionProtector to protect it
    #@ActionProtector(has_permission('view_photos'))
    def galleria(self, page=None):
        photo_q = Session.query(PyGallPhoto).order_by(PyGallPhoto.time.asc())
        if page is None:
            # default to last page
            page = int(ceil(float(photo_q.count()) / 33))
            redirect(url(controller='photos', action='galleria', page=page))

        c.photos = paginate.Page(photo_q, page=page, items_per_page=33)
        c.edit = bool(request.params.get('edit', False))
        return render('/pygall/photos/galleria.mako.html')
