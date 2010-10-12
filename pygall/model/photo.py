from sqlalchemy import Table, Sequence, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, mapper

from pygall.model.meta import metadata

pygall_photos_table = Table(
    "photos", metadata,
    Column('id', Integer, Sequence('photos_seq', optional=True),
              primary_key=True),
    Column("uri", Unicode, nullable=False),
    Column("md5sum", Unicode, unique=True),
    Column("description", Unicode),
    Column("rating", Integer),
    Column("time", DateTime, nullable=False),
)
# id, uri, description, rating, time

pygall_tags_table = Table(
    "tags", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Unicode, nullable=False)
)
# id, name

pygall_photos_tags_table = Table(
    "photo_tags", metadata,
    Column("photo_id", Integer, ForeignKey('photos.id')),
    Column("tag_id", Integer, ForeignKey('tags.id'))
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

mapper(PyGallTag,
       pygall_tags_table,
       properties = {
           'photos' : relation(PyGallPhoto, secondary = pygall_photos_tags_table),
        })

mapper(PyGallPhoto,
       pygall_photos_table,
       properties = {
          'tags' : relation(PyGallTag, secondary = pygall_photos_tags_table),
       })

