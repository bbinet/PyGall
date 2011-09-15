from formalchemy import Grid, FieldSet, config
from pyramid_formalchemy.utils import TemplateEngine
from fa.jquery import renderers as fa_renderers

from pygall import models
from pygall.lib.formalchemy.pygallimage import PyGallImageFieldRenderer

config.engine = TemplateEngine()

FieldSet.default_renderers.update(fa_renderers.default_renderers)

Tag = FieldSet(models.Tag)
Tag.configure(exclude=[Tag.photos])
TagGrid = Grid(models.Tag)
TagGrid.configure(exclude=[TagGrid.photos])

PhotoView = FieldSet(models.Photo)
PhotoView.fspot_id.set(readonly=True)
PhotoView.md5sum.set(readonly=True)
PhotoView.uri.set(renderer=PyGallImageFieldRenderer)
PhotoView.configure()

PhotoEdit = FieldSet(models.Photo)
PhotoEdit.fspot_id.set(readonly=True)
PhotoEdit.md5sum.set(readonly=True)
PhotoEdit.uri.set(renderer=PyGallImageFieldRenderer, readonly=True)
PhotoEdit.configure()

PhotoAdd = FieldSet(models.Photo)
PhotoAdd.uri.set(renderer=PyGallImageFieldRenderer)
PhotoAdd.configure(exclude=[
    PhotoAdd.fspot_id, PhotoAdd.md5sum, PhotoAdd.time])

PhotoGrid = Grid(models.Photo)
PhotoGrid.configure(exclude=[PhotoGrid.md5sum])

