# Define mapping for f-spot database
# This is used by the script to synchronize pygall with fspot

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation, column_property
from sqlalchemy.sql import and_
from sqlalchemy import Table, Column, Sequence, DateTime, Integer, Unicode, ForeignKey

DBSession = scoped_session(sessionmaker(autoflush = True, autocommit = False))
Base = declarative_base()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

photos_tags_table = Table(
    "photo_tags", Base.metadata,
    Column("photo_id", Integer, ForeignKey('photos.id')),
    Column("tag_id", Integer, ForeignKey('tags.id'))
)
# photo_id, tag_id

class Tag(Base):

    __tablename__ = 'tags'

    # Columns
    # id, name, category_id, is_category, sort_priority, icon
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

    # Relations
    photos = relation('Photo', secondary=photos_tags_table)
    #icon = deferred(icon), # Big: ignore!

    def __init__(self, name):
        self.name = name


class PhotoVersion(Base):

    __tablename__ = 'photo_versions'

    # Columns
    # photo_id, version_id, name, base_uri, filename, md5_sum, protected
    photo_id = Column(Integer(), ForeignKey('photos.id'), primary_key=True)
    version_id = Column(Integer(), primary_key=True)
    base_uri = Column(Unicode())
    filename = Column(Unicode())
    uri = column_property(base_uri + filename)

class Photo(Base):

    __tablename__ = 'photos'

    # Columns
    # id, time, base_uri, filename, description, roll_id, default_version_id,
    # rating, md5_sum
    id = Column(Integer, Sequence('photos_seq', optional=True),
            primary_key=True)
    base_uri = Column(Unicode())
    filename = Column(Unicode())
    uri = column_property(base_uri + filename)
    description = Column(Unicode)
    rating = Column(Integer)
    default_version_id = Column(Integer)
    time = Column(Integer, nullable=False)

    # Relations
    tags = relation('Tag', secondary=photos_tags_table, lazy=False)
    last_version = relation(PhotoVersion,
            primaryjoin=and_(
                id==PhotoVersion.photo_id,
                default_version_id==PhotoVersion.version_id),
            uselist=False,
            lazy=False)

