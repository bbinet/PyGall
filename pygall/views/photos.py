import logging
import cgi
import os
import shutil
from math import ceil
from tempfile import mkdtemp
from shutil import rmtree

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.exceptions import NotFound
from pyramid.security import authenticated_userid
from webhelpers.paginate import Page
from archive import extract, UnrecognizedArchiveFormat

from pygall.models import DBSession, Photo
from pygall.lib.imageprocessing import ip
from pygall.lib.helpers import img_md5, get_size


log = logging.getLogger(__name__)

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
        if DBSession.query(Photo).filter_by(uri=uri).delete() == 0:
            raise NotFound()
        ip.remove_image(uri)
        log.debug('ip.remove_image(%s)' % uri)
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
            try:
                fn = f.filename
                extract(f.file, tmpdir, safe=True, filename=fn)
                log.debug("file '%s' has been correctly extracted" % fn)
            except UnrecognizedArchiveFormat as e:
                # seems to be a single file, save it
                try:
                    fdst = open(
                            os.path.join(tmpdir, os.path.basename(fn)), 'wb')
                    shutil.copyfileobj(f.file, fdst)
                    log.debug("file '%s' has been correctly copied" % fn)
                finally:
                    if fdst: fdst.close()

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
                        if isinstance(info, Photo):
                            uri = info.uri
                            _ = self.request.translate
                            result["error"] = _('File already exists on server')
                        else:
                            uri = info['uri']

                        result["url"] = self.request.static_path(
                            settings['photos_dir']+'/orig/' + uri),
                        result["thumbnail_url"] = self.request.static_path(
                            settings['photos_dir']+'/scaled/' + uri),
                        result["delete_url"] = self.request.route_path(
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
        photo = DBSession.query(Photo).filter_by(md5sum=hash)
        if photo.count() > 0:
            log.info("Same md5sum already exists in database")
            return photo.first()

        # process and import photos to public/data/photos dir
        info = ip.process_image(abspath, md5sum=hash)
        os.unlink(abspath)

        # import image in db
        photo = Photo()
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
            'debug': self.debug,
            'logged_in': authenticated_userid(self.request),
            'maxfilesize': settings.get('upload_maxsize', 10000000),
            'minfilesize': settings.get('upload_minsize', 50000),
        }


    @view_config(route_name='photos_index', renderer='galleria.html.mako',
            permission='view')
    def index(self):
        page = self.request.matchdict.get('page')
        photo_q = DBSession.query(Photo).order_by(Photo.time.asc())
        if page == '':
            # default to last page
            page = int(ceil(float(photo_q.count()) / 20))
            params = [('debug', 1)] if self.debug else []
            return HTTPFound(
                    location=self.request.route_path('photos_index', page=page, _query=params))

        # Inside a view method -- ``self`` comes from the surrounding scope.
        def url_generator(page):
            return self.request.route_path('photos_index', page=page)
        photos = Page(photo_q, page=page, items_per_page=20, url=url_generator)
        return {
            'debug': self.debug,
            'logged_in': authenticated_userid(self.request),
            'photos': photos,
            'photos_dir': self.request.registry.settings['photos_dir'],
        }

    @view_config(route_name='photos_query', renderer='jsonp', permission='view')
    def query(self):
        photos_dir = self.request.registry.settings['photos_dir']
        page = int(self.request.params.get('page', 1))
        maxphotos = int(self.request.params.get('max', 30))
        photo_q = DBSession.query(Photo).order_by(Photo.time.asc())
        photos = Page(photo_q, page=page, items_per_page=maxphotos)
        return {
                'meta': {
                    'page': page,
                    'page_count': photos.page_count,
                    },
                'photos': [{
                    'image': self.request.static_url(photos_dir+'/scaled/'+str(p.uri)),
                    'title': 'mon titre'
                    } for p in photos],
                }
