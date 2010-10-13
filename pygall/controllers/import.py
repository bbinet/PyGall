import logging
import os

from pylons import config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector

from pygall.lib.base import BaseController, render
from pygall.lib.helpers import unchroot_path, remove_empty_dirs
from pygall.lib.archivefile import extractall

log = logging.getLogger(__name__)

class ImportController(BaseController):

    @ActionProtector(has_permission('admin'))
    def upload(self):
        """POST /photos/upload: Upload archive of photo"""
        # url(controller='import', action='upload')

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

        try:
            # extract archive to "import" directory
            extractall(filepath, config['app_conf']['import_dir'])

            # walk in import directory to delete all files that are not photos
            for dirpath, dirs, files in os.walk(
                config['app_conf']['import_dir'], topdown=False):
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

    @ActionProtector(has_permission('admin'))
    def index(self):
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
        return render('/pygall/import/index.mako.html')

    @ActionProtector(has_permission('admin'))
    def new(self, format='html'):
        """GET /import/new: Form to create a new item"""
        return render('/pygall/import/new.mako.html')

    @ActionProtector(has_permission('admin'))
    @jsonify
    def delete(self):
        """GET /import/delete: Delete an existing item"""
        error = False
        msg = None
        uri = None
        try:
            abspath, uri = unchroot_path(
                request.params.get('path', None),
                config['app_conf']['import_dir'])
            os.unlink(abspath)
            msg = "File has been successfully deleted"
            remove_empty_dirs(config['app_conf']['import_dir'])
        except Exception, e:
            error = True
            msg = str(e)
            log.error(msg)
        return {
            "path": uri,
            "status": not error,
            "msg": msg
        }
