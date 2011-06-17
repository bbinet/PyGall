import logging
import os
from math import ceil
from tempfile import mkdtemp
from shutil import rmtree

from pyramid.view import view_config
from pyramid.i18n import get_locale_name
from pyramid.asset import abspath_from_asset_spec
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.exceptions import NotFound, Forbidden
from pyramid.security import remember, forget, authenticated_userid
from pyramid.url import route_url
from webhelpers.paginate import Page

from pygall.models import DBSession, PyGallTag, PyGallPhoto
from pygall.lib.imageprocessing import ImageProcessing
from pygall.lib.archivefile import extractall
from pygall.lib.helpers import md5_for_file, unchroot_path, remove_empty_dirs
from pygall.security import authenticate

log = logging.getLogger(__name__)


@view_config(context=Forbidden)
def forbidden_view(request):
    if not authenticated_userid(request):
        return HTTPFound(location = route_url('login', request))
    return Forbidden()

@view_config(route_name='login', renderer='login.html.mako')
def login(request):
    referrer = request.url
    login_url = route_url('login', request)
    if referrer == login_url:
        # never use the login form itself as came_from
        referrer = route_url('photos_index', request, page='')
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login'].strip()
        password = request.params['password']
        if authenticate(login, password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = login_url,
        #url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        #password = password,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = route_url('login', request),
                     headers = headers)


class Photos(object):
    def __init__(self, request):
        self.request = request
        self.debug = "debug" in request.params
        self.lang = get_locale_name(request)
        self.ip = ImageProcessing(request.registry.settings['photos_dir'])

    @view_config(route_name='photos_create', renderer='json',
            permission='edit')
    def create(self):
        """POST /photos: Create a new item"""
        log.error("create")

        # gp.fileupload stores uploaded filename in fieldstorage
        fieldstorage = self.request.params.get('file', u'')
        if fieldstorage == u'':
            log.debug("Nothing uploaded")
            return HTTPBadRequest()
        upload_dir = self.request.registry.settings['upload_dir']
        filepath = os.path.join(
                upload_dir,
                fieldstorage.file.read().strip(" \n\r"))
        log.debug("File has been downloaded to %s" %(filepath))
        fieldstorage.file.close()

        # extract to a tmpdir that we should delete immediately
        # after import is done.
        tmpdir = mkdtemp(dir=upload_dir)

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
        photo = DBSession.query(PyGallPhoto).filter_by(md5sum=hash)
        if photo.count() > 0:
            raise Exception("Same md5sum already exists in database")

        # process and import photos to public/data/photos dir
        try:
            date, dest_uri = self.ip.process_image(abspath)
        except Exception as e:
            self.ip.remove_image(abspath)
            raise e

        # import image in db
        photo = PyGallPhoto()
        photo.uri = dest_uri
        photo.md5sum = hash
        photo.time = date
        DBSession.add(photo)
        DBSession.flush()

    @view_config(route_name='photos_new', renderer='new.html.mako',
            permission='edit')
    def new(self, format='html'):
        """GET /photos/new: Form to create a new item"""
        return {
            'logged_in': authenticated_userid(self.request)
        }

    @view_config(route_name='photos_editcomment', renderer='json')
    def editcomment(self):
        uri = self.request.params.getone('uri')
        comment = self.request.params.getone('comment')
        photo = DBSession.query(PyGallPhoto).filter_by(uri=uri).first()
        if not photo:
            raise NotFound()
        photo.description = comment
        DBSession.flush()
        return {
            'status': 0,
            'msg': 'OK'
        }


    @view_config(route_name='photos_index', renderer='galleria.html.mako',
            permission='view')
    def index(self):
        page = self.request.matchdict.get('page')
        photo_q = DBSession.query(PyGallPhoto).order_by(PyGallPhoto.time.asc())
        if page == '':
            # default to last page
            page = int(ceil(float(photo_q.count()) / 33))
            return HTTPFound(
                    location=self.request.route_url('photos_index', page=page))

        # Inside a view method -- ``self`` comes from the surrounding scope.
        def url_generator(page):
            return self.request.route_url('photos_index', page=page)
        photos = Page(photo_q, page=page, items_per_page=33, url=url_generator)
        edit = bool(self.request.params.get('edit', False))
        return {
            'logged_in': authenticated_userid(self.request),
            'photos': photos,
            'edit': edit
        }
