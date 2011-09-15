from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from sqlalchemy import Table, Sequence, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation
import sqlahelper

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

photos_tags_table = Table(
    "photo_tags", Base.metadata,
    Column("photo_id", Integer, ForeignKey('photos.id')),
    Column("tag_id", Integer, ForeignKey('tags.id'))
)
# photo_id, tag_id


class Tag(Base):

    __acl__ = [(Allow, 'admin', ALL_PERMISSIONS)]
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

    # Relations
    photos = relation('Photo', secondary=photos_tags_table)

    def __init__(self, name=None):
        self.name = name

    def __unicode__(self):
        return u'[%s]' % self.name


class Photo(Base):

    __acl__ = [(Allow, 'admin', ALL_PERMISSIONS)]
    __tablename__ = 'photos'

    # Columns
    id = Column(Integer, Sequence('photos_seq', optional=True),
            primary_key=True)
    fspot_id = Column(Integer, nullable=True, unique=True)
    uri = Column(Unicode, unique=True, nullable=False, index=True)
    md5sum = Column(Unicode, unique=True)
    description = Column(Unicode)
    rating = Column(Integer)
    time = Column(DateTime)

    # Relations
    tags = relation('Tag', secondary=photos_tags_table)

    def __unicode__(self):
        return u'[%s]' % self.uri

