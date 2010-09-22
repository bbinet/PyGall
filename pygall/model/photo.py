import sqlalchemy as sa
from sqlalchemy import orm
from pygall.model import meta

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

