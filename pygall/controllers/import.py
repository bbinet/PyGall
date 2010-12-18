import logging
import os

from pylons import config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector

from pygall.lib.base import BaseController, render
from pygall.lib.helpers import unchroot_path, remove_empty_dirs

log = logging.getLogger(__name__)

class ImportController(BaseController):

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
