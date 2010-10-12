from sqlalchemy import Table, Sequence, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, mapper

from pygall.model.meta import Base


photos_tags_table = Table(
    "photo_tags", Base.metadata,
    Column("photo_id", Integer, ForeignKey('photos.id')),
    Column("tag_id", Integer, ForeignKey('tags.id'))
)
# photo_id, tag_id


class PyGallTag(Base):

    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

    # Relations
    photos = relation('PyGallPhoto', secondary=photos_tags_table)

    def __init__(self, name):
        self.name = name


class PyGallPhoto(Base):

    __tablename__ = 'photos'

    # Columns
    id = Column(Integer, Sequence('photos_seq', optional=True),
            primary_key=True)
    uri = Column(Unicode, nullable=False)
    md5sum = Column(Unicode, unique=True)
    description = Column(Unicode)
    rating = Column(Integer)
    time = Column(DateTime, nullable=False)

    # Relations
    tags = relation('PyGallTag', secondary=photos_tags_table)

    def __init__(self, fspot_photo=None):
        if fspot_photo is not None:
            self.uri = fspot_uri_to_pygall(fspot_photo.uri)
            self.md5sum = fspot_photo.md5sum
            self.description = fspot_photo.description
            self.rating = fspot_photo.rating
            self.time = datetime.fromtimestamp(fspot_photo.time) # Convert to datetime

