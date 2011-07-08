import cgi

from formalchemy.fields import FieldRenderer, FileFieldRenderer
from formalchemy.ext.fsblob import ImageFieldRenderer

from pygall.lib.imageprocessing import ImageProcessing

class PyGallImageFieldRenderer(ImageFieldRenderer):

    def __init__(self, *args, **kwargs):
        FileFieldRenderer.__init__(self, *args, **kwargs)
        self.ip = ImageProcessing(self.request.registry.settings['photos_dir'])
        self._path = None

    @property
    def storage_path(self):
        return self.request.registry.settings['photos_dir']

    def get_url(self, relative_path):
        """ override ImageFieldRenderer get_url """
        return self.request.route_url('photos/',
                subpath='/scaled/%s' % relative_path)

    def deserialize(self):
        """ override ImageFieldRenderer deserialize """
        if self._path:
            return self._path
        data = FieldRenderer.deserialize(self)
        if isinstance(data, cgi.FieldStorage):
            _, self._path = self.ip.process_image(data.file)
            return self._path
        checkbox_name = '%s--remove' % self.name
        if not data and not self.params.has_key(checkbox_name):
            data = getattr(self.field.model, self.field.name)
        return self._path

