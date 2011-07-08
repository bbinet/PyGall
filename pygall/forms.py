from formalchemy import Grid, FieldSet, config
from pyramid_formalchemy.utils import TemplateEngine
from fa.jquery import renderers as fa_renderers

from pygall import models
from pygall.lib.formalchemy.pygallimage import PyGallImageFieldRenderer

config.engine = TemplateEngine()

FieldSet.default_renderers.update(fa_renderers.default_renderers)

PyGallTag = FieldSet(models.PyGallTag)
PyGallTag.configure(exclude=[PyGallTag.photos])
PyGallTagGrid = Grid(models.PyGallTag)
PyGallTagGrid.configure(exclude=[PyGallTagGrid.photos])

PyGallPhotoView = FieldSet(models.PyGallPhoto)
PyGallPhotoView.fspot_id.set(readonly=True)
PyGallPhotoView.md5sum.set(readonly=True)
PyGallPhotoView.uri.set(renderer=PyGallImageFieldRenderer)
PyGallPhotoView.configure()

PyGallPhotoEdit = FieldSet(models.PyGallPhoto)
PyGallPhotoEdit.fspot_id.set(readonly=True)
PyGallPhotoEdit.md5sum.set(readonly=True)
PyGallPhotoEdit.uri.set(renderer=PyGallImageFieldRenderer, readonly=True)
PyGallPhotoEdit.configure()

PyGallPhotoAdd = FieldSet(models.PyGallPhoto)
PyGallPhotoAdd.uri.set(renderer=PyGallImageFieldRenderer)
PyGallPhotoAdd.configure(exclude=[
    PyGallPhotoAdd.fspot_id, PyGallPhotoAdd.md5sum, PyGallPhotoAdd.time])

PyGallPhotoGrid = Grid(models.PyGallPhoto)
PyGallPhotoGrid.configure(exclude=[PyGallPhotoGrid.md5sum])

