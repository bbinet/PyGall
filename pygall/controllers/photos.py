import logging
import os
from math import ceil
from webhelpers import paginate
from types import StringType, UnicodeType

from pylons import config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify

from pygall.lib.base import BaseController, render
from pygall.lib.archivefile import extractall
from pygall.lib.imageprocessing import ImageProcessing
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class PhotosController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('photo', 'photos')

    # get safe and correct unchroot path
    def _unchroot_path(self, path, chroot):
        if type(path) != StringType and type(path) != UnicodeType:
            raise Exception('Bad path (type is not string)')
        while path.startswith(os.sep):
            path = path[len(os.sep):]
        if not path.startswith(os.path.basename(chroot)):
            raise Exception('Bad path (no chroot prefix)')

        uri = os.path.normpath(path[len(os.path.basename(chroot)):])
        while uri.startswith(os.sep):
            uri = uri[len(os.sep):]
        unchroot_path = os.path.normpath(os.path.join(chroot, uri))

        if not unchroot_path.startswith(chroot):
            raise Exception('Bad path (chroot protected)')
        if not os.path.exists(unchroot_path):
            raise Exception('Bad path (does not exist): %s' %unchroot_path)

        return (unchroot_path, uri)


    def upload(self):
        """POST /photos/upload: Upload archive of photo"""
        # url(controller='photos', action='upload')

        # gp.fileupload stores uploaded filename in fieldstorage
        fieldstorage = request.POST['file']
        filepath = os.path.join(
            config['global_conf']['upload_dir'],
            fieldstorage.file.read().strip(" \n\r"))
        log.debug("File has been downloaded to %s" %(filepath))
        fieldstorage.file.close()

        try:
            # extract archive to "import" directory
            extractall(filepath, config['app_conf']['import_dir'])

            # walk in import directory to delete all files that are not photos
            for dirpath, dirs, files in os.walk(config['app_conf']['import_dir'], topdown=False):
                for filename in files:
                    abspath = os.path.join(dirpath, filename)
                    log.debug("walk on file: %s" %abspath)
                    if os.path.splitext(abspath)[1].lower() not in ['.jpg', '.jpeg']:
                        log.debug("Remove non jpeg file: %s" %abspath)
                        os.remove(abspath)
                for subdirname in dirs:
                    abspath = os.path.join(dirpath, subdirname)
                    log.debug("walk on dir: %s" %abspath)
                    try:
                        os.rmdir(abspath)
                    except OSError:
                        log.debug('directory is not empty')
            log.debug("Extraction to %s has succeeded" %(config['app_conf']['import_dir']))
        except Exception, e:
            # TODO: log error in session (flash message)
            raise e
        # delete the uploaded archive if no exception is raised
        os.remove(filepath)

    def import_(self):
        """GET /photos/import: Choose photos to be imported"""
        # create a json tree of the photos to be imported
        c.tree = []
        import_dir = config['app_conf']['import_dir']
        while import_dir.endswith(os.sep):
            import_dir = import_dir[:-len(os.sep)]
        cut, basename = os.path.split(import_dir)
        c.tree.append(basename + os.sep)
        for root, dirs, files in os.walk(import_dir, topdown=True):
            for name in files:
                c.tree.append(os.path.join(root, name)[len(cut)+1:])
            for name in dirs:
                c.tree.append(os.path.join(root, name)[len(cut)+1:] + os.sep)
        c.tree.sort()
        return render('/photos/import.mako.html')

    def index(self, format='html'):
        """GET /photos: All items in the collection"""
        # url('photos')

    @jsonify
    def create(self):
        """POST /photos: Create a new item"""
        # url('photos')
        abspath, uri = self._unchroot_path(
            request.params.get('path', None),
            config['app_conf']['import_dir'])

        ip = ImageProcessing(
            config['app_conf']['import_dir'],
            os.path.join(
                config['pylons.paths']['static_files'],
                config['app_conf']['photos_public_dir']))

        error = False
        msg = None
        try:
            # TODO: check same image has not already been imported
            ip.process_image(uri)
            # TODO: import image in db
            # remove empty directories
            for dirpath, dirs, files in os.walk(
                config['app_conf']['import_dir'],
                topdown=False):
                for subdirname in dirs:
                    try:
                        os.rmdir(os.path.join(dirpath, subdirname))
                    except OSError:
                        log.debug('directory is not empty')
        except Exception, e:
            error = True
            msg = str(e)
            log.error(msg)

        return {
            "status": not error,
            "msg": msg
        }

    def new(self, format='html'):
        """GET /photos/new: Form to create a new item"""
        # url('new_photo')
        return render('/photos/new.mako.html')

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
