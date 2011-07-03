from formalchemy import Grid, FieldSet, config
from pyramid_formalchemy.utils import TemplateEngine
from fa.jquery import renderers as fa_renderers

from pygall import models

config.engine = TemplateEngine()

FieldSet.default_renderers.update(fa_renderers.default_renderers)

PyGallTag = FieldSet(models.PyGallTag)
PyGallTag.configure(exclude=[PyGallTag.photos])
PyGallTagGrid = Grid(models.PyGallTag)
PyGallTagGrid.configure(exclude=[PyGallTagGrid.photos])

PyGallPhoto = FieldSet(models.PyGallPhoto)
PyGallPhoto.fspot_id.set(readonly=True)
PyGallPhoto.uri.set(readonly=True)
PyGallPhoto.md5sum.set(readonly=True)
PyGallPhoto.configure()
PyGallPhotoGrid = Grid(models.PyGallPhoto)
PyGallPhotoGrid.configure(exclude=[PyGallPhotoGrid.md5sum])

