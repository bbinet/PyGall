import logging
import cgi
import os
from math import ceil
from tempfile import mkdtemp
from shutil import rmtree

from pyramid.view import view_config
from pyramid.asset import abspath_from_asset_spec
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.exceptions import NotFound, Forbidden
from pyramid.security import remember, forget, authenticated_userid
from pyramid.url import route_url
from webhelpers.paginate import Page

from pygall.models import DBSession, PyGallTag, PyGallPhoto
from pygall.lib.imageprocessing import ip
from pygall.lib.archivefile import extractall
from pygall.lib.helpers import img_md5, unchroot_path, remove_empty_dirs, get_size
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

    @view_config(route_name='photos_delete', renderer='json',
            permission='edit')
    def delete(self):
        """POST /photos/delete: Create a new item"""
        uri = self.request.params.get('uri', None)
        if not uri:
            return HTTPBadRequest()
        if DBSession.query(PyGallPhoto).filter_by(uri=uri).delete() == 0:
            raise NotFound()
        ip.remove_image(uri)
        remove_empty_dirs(self.request.registry.settings['upload_dir'], uri)
        return True

    @view_config(route_name='photos_create', renderer='json',
            permission='edit', request_method='POST')
    def create(self):
        """POST /photos: Create a new item"""

        f = self.request.params.get('files[]', None)
        if not isinstance(f, cgi.FieldStorage):
            return HTTPBadRequest()

        done = []
        settings = self.request.registry.settings
        # extract to a tmpdir that we should delete immediately
        # after import is done.
        tmpdir = mkdtemp(dir=settings['upload_dir'])

        try:
            extractall(f.file, tmpdir, name=f.filename)

            # walk in import directory to import all image files
            for dirpath, dirs, files in os.walk(tmpdir, topdown=False):
                for filename in files:
                    abspath = os.path.join(dirpath, filename)
                    log.debug("Importing image: %s" % abspath)
                    try:
                        info = self._import(abspath)
                        result = {
                            "name": f.filename,
                            "size": get_size(f.file),
                            "delete_type":"DELETE",
                            }
                        uri = None
                        if isinstance(info, PyGallPhoto):
                            uri = info.uri
                            _ = self.request.translate
                            result["error"] = _('File already exists on server')
                        else:
                            uri = info['uri']

                        result["url"] = self.request.static_url(
                            settings['photos_dir']+'/orig/' + uri),
                        result["thumbnail_url"] = self.request.static_url(
                            settings['photos_dir']+'/scaled/' + uri),
                        result["delete_url"] = self.request.route_url(
                            'photos_delete', _query=[('uri', uri)]),
                        done.append(result)
                    except Exception as e:
                        # TODO: log error in session (flash message)
                        log.exception("Error while importing image, skip" \
                                "file: %s" % abspath)
        except Exception, e:
            # TODO: log error in session (flash message)
            raise e
        finally:
            rmtree(tmpdir)

        return done


    def _import(self, abspath):
        # check same image has not already been imported
        hash = img_md5(abspath)
        photo = DBSession.query(PyGallPhoto).filter_by(md5sum=hash)
        if photo.count() > 0:
            log.info("Same md5sum already exists in database")
            return photo.first()

        # process and import photos to public/data/photos dir
        info = ip.process_image(abspath, md5sum=hash)
        os.unlink(abspath)

        # import image in db
        photo = PyGallPhoto()
        photo.uri = info['uri']
        photo.md5sum = hash
        photo.time = info['date']
        DBSession.add(photo)
        DBSession.flush()

        return info


    @view_config(route_name='photos_new', renderer='new.html.mako',
            permission='edit', request_method='GET')
    def new(self, format='html'):
        """GET /photos/new: Form to create a new item"""
        settings = self.request.registry.settings
        return {
            'logged_in': authenticated_userid(self.request),
            'maxfilesize': settings.get('upload_maxsize', 10000000),
            'minfilesize': settings.get('upload_minsize', 50000),
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
            'photos_dir': self.request.registry.settings['photos_dir'],
            'edit': edit
        }
