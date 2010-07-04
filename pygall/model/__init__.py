"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from pygall.model import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    meta.Session.configure(bind=engine)
    meta.engine = engine


############################################################
# PyGall database
############################################################

pygall_photos_table = sa.Table(
    "photos", meta.metadata,
    sa.Column('id', sa.types.Integer, sa.Sequence('photos_seq', optional=True),
              primary_key=True),
    sa.Column("uri", sa.types.Unicode, nullable=False),
    sa.Column("md5sum", sa.types.Unicode, unique=True),
    sa.Column("description", sa.types.Unicode),
    sa.Column("rating", sa.types.Integer),
    sa.Column("time", sa.types.DateTime, nullable=False),
)
# id, uri, description, rating, time

pygall_tags_table = sa.Table(
    "tags", meta.metadata,
    sa.Column("id", sa.types.Integer, primary_key=True),
    sa.Column("name", sa.types.Unicode, nullable=False)                                                                                                                                                  
)
# id, name

pygall_photos_tags_table = sa.Table(
    "photo_tags", meta.metadata,
    sa.Column("photo_id", sa.types.Integer, sa.ForeignKey('photos.id')),
    sa.Column("tag_id", sa.types.Integer, sa.ForeignKey('tags.id'))
)
# photo_id, tag_id

class PyGallTag(object):
    def __init__(self, name):
        self.name = name

class PyGallPhoto(object):
    def __init__(self, fspot_photo=None):
        if fspot_photo is not None:
            self.uri = fspot_uri_to_pygall(fspot_photo.uri)
            self.md5sum = fspot_photo.md5sum
            self.description = fspot_photo.description
            self.rating = fspot_photo.rating
            self.time = datetime.fromtimestamp(fspot_photo.time) # Convert to datetime

orm.mapper(PyGallTag,
       pygall_tags_table,
       properties = {
           'photos' : orm.relation(PyGallPhoto, secondary = pygall_photos_tags_table),
        })

orm.mapper(PyGallPhoto,
       pygall_photos_table,
       properties = {
          'tags' : orm.relation(PyGallTag, secondary = pygall_photos_tags_table),
       })


#############################################################
## F-Spot database
#############################################################
#
#fspot_tags_table = sa.Table(
#    "tags", meta.metadata,
#    sa.Column("id", sa.types.Integer, primary_key=True),
#    sa.Column("name", sa.types.Unicode, nullable=False),
#    sa.Column("category_id", sa.types.Integer, sa.ForeignKey('tags.id')),
#    sa.Column("is_category", sa.types.Boolean),
#    sa.Column("sort_priority", sa.types.Integer),
#    sa.Column("icon", sa.types.Unicode)
#)
## id, name, category_id, is_category, sort_priority, icon
#
#fspot_photo_tags_table = sa.Table(
#    "photo_tags", meta.metadata,
#    sa.Column("photo_id", sa.types.Integer, sa.ForeignKey('photos.id')),
#    sa.Column("tag_id", sa.types.Integer, sa.ForeignKey('tags.id'))
#)
## photo_id, tag_id
#
#fspot_photos_table = sa.Table(
#    "photos", meta.metadata,
#    sa.Column("id", sa.types.Integer, primary_key=True),
#    sa.Column("time", sa.types.Integer, nullable=False),
#    sa.Column("uri", sa.types.Unicode, nullable=False),
#    sa.Column("description", sa.types.Unicode),
#    sa.Column("roll_id", sa.types.Integer),
#    sa.Column("default_version_id", sa.types.Integer),
#    sa.Column("rating", sa.types.Integer)
#)
## id, time, uri, description, roll_id, default_version_id, rating
#
#class FSpotTag(object):
#    pass
#class FSpotPhoto(object):
#    pass
#
#orm.mapper(FSpotTag,
#       fspot_tags_table,
#       properties = {
#        'icon' : orm.deferred(fspot_tags_table.c.icon), # Big
#        'photos' : orm.relation(FSpotPhoto, secondary = fspot_photo_tags_table),
#        })
#orm.mapper(FSpotPhoto,
#       fspot_photos_table,
#       properties = {
#          'tags' : orm.relation(FSpotTag, secondary = fspot_photo_tags_table),
#          })

