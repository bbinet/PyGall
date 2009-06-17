#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copy picture tags from F-Spot database to DigiKam
#
# Quick way to check the tables structure:
#
#   $ sqlite3 ~/.gnome2/f-spot/photos.db
#   sqlite> .tables
#   ...
#   sqlite> .schema tags
#   ...

import os

home = os.environ['HOME']
fspot_db = "sqlite:////%(home)s/.gnome2/f-spot/photos.db" % locals()
digikam_db = "sqlite:////%(home)s/Obrazki/digikam3.db" % locals()

# Prefix to remove from F-Spot urls to get the digikam URLs.
fspot_mount = r'file:///home/marcin/Pictures'

ECHO_DB = False

############################################################

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, Table, \
     DateTime, UnicodeText, Integer, String, Unicode, ForeignKey
from sqlalchemy.sql import func, join
from sqlalchemy.orm import mapper, sessionmaker, deferred, backref, relation
from sqlalchemy.exceptions import InvalidRequestError

############################################################
# F-Spot database
############################################################

fspot_engine = create_engine(fspot_db, echo=ECHO_DB)
fspot_metadata = MetaData()

fspot_tags_table = Table(
    "tags", fspot_metadata,
    Column("name", Unicode()),
    autoload = True, autoload_with = fspot_engine)
# id, name, category_id, is_category, sort_priority, icon

fspot_photo_tags_table = Table(
    "photo_tags", fspot_metadata,
    Column("photo_id", Integer, ForeignKey('photos.id')),
    Column("tag_id", Integer, ForeignKey('tags.id')),
    autoload = True, autoload_with = fspot_engine)
# photo_id, tag_id

fspot_photos_table = Table(
    "photos", fspot_metadata,
    Column("uri", Unicode()),
    autoload = True, autoload_with = fspot_engine)
# id, time, uri, description, roll_id, default_version_id, rating

class FSpotTag(object):
    pass
class FSpotPhoto(object):
    pass

mapper(FSpotTag,
       fspot_tags_table,
       properties = {
        'icon' : deferred(fspot_tags_table.c.icon), # Big
        'photos' : relation(FSpotPhoto, secondary = fspot_photo_tags_table),
        })
mapper(FSpotPhoto,
       fspot_photos_table,
       properties = {
          'tags' : relation(FSpotTag, secondary = fspot_photo_tags_table),
          })

############################################################
# Digikam database
############################################################

digikam_engine = create_engine(digikam_db, echo=ECHO_DB)
digikam_metadata = MetaData()

digikam_images_table = Table(
    "Images", digikam_metadata,
    Column("name", Unicode()),
    Column("dirid", Integer(), ForeignKey("Albums.id")),
    Column("datetime", Unicode()), # I had problems with data format
    autoload = True, autoload_with = digikam_engine)
# id, name, dirid, caption, datetime

digikam_albums_table = Table(
    "Albums", digikam_metadata,
    Column("url", Unicode()),
    Column("date", Unicode()), 
    autoload = True, autoload_with = digikam_engine)
# id, url, date, caption(NULL), collection(NULL), icon(NULL)

digikam_tags_table = Table(
    "Tags", digikam_metadata,
    Column("name", Unicode()),
    autoload = True, autoload_with = digikam_engine)
# id, pid, name, icon, iconkde

digikam_image_tags_table = Table(
    "ImageTags", digikam_metadata,
    Column("imageid", Integer, ForeignKey('Images.id')),
    Column("tagid", Integer, ForeignKey('Tags.id')),
    autoload = True, autoload_with = digikam_engine)
# imageid, tagid

class DigikamTag(object):
    def __init__(self, name):
        self.name = name
        self.iconkde = "tag"
        self.pid = 0

class DigikamPhoto(object):
    pass

mapper(DigikamTag,
       digikam_tags_table,
       properties = {
        'icon' : deferred(digikam_tags_table.c.icon),
        'photos' : relation(DigikamPhoto, secondary = digikam_image_tags_table),
        })

mapper(DigikamPhoto,
       digikam_images_table.join(digikam_albums_table),
       properties = {
          'tags' : relation(DigikamTag, secondary = digikam_image_tags_table),
          # I do not use this column and I had problems decoding them
          # on some photos (invalid utf-8)
          'caption' : deferred(digikam_images_table.c.caption),
          })


############################################################
# Connect to the database
############################################################

FSpotSession = sessionmaker(autoflush = True, transactional = True)
FSpotSession.configure(bind = fspot_engine)
DigikamSession = sessionmaker(autoflush = True, transactional = True)
DigikamSession.configure(bind = digikam_engine)

fspot_session = FSpotSession()
digikam_session = DigikamSession()

############################################################
# Creating missing tags and caching them
############################################################

digikam_tags = {}

for f_tag in fspot_session.query(FSpotTag).all():
    d_tag = digikam_session.query(DigikamTag).filter_by(name = f_tag.name).first()
    if not d_tag:
        print "Creating missing Digikam tag %s" % f_tag.name
        d_tag = DigikamTag(f_tag.name)
        digikam_session.save(d_tag)

    digikam_tags[ f_tag.name ] = d_tag

############################################################
# Copying image tags
############################################################

import os.path
def fspot_uri_to_digikam(f_uri):
    """
    Takes F-Spot file uri. Returns the tuple (dir-uri, filename)
    to be used on Digikam
    """
    if not f_uri.startswith(fspot_mount):
        raise Exception("Don't know how to handle image %s" % f_uri)
    rest = f_uri.replace(fspot_mount, "")
    return (os.path.dirname(rest), os.path.basename(rest))

# Note: I have only minority of my photos tagged. Therefore
# I prefer to iterate starting from tags. With well tagged
# collection it may be better to iterate over photos, then tags

for f_tag in fspot_session.query(FSpotTag).all():
    d_tag = digikam_tags[ f_tag.name ]
    for f_photo in f_tag.photos:
        # Lookup the same photo in Digikam database
        (d_album_uri, d_photo_name) = fspot_uri_to_digikam(f_photo.uri)
        try:
            d_photo = digikam_session.query(DigikamPhoto).filter_by(
                name = d_photo_name, url = d_album_uri).one()
        except InvalidRequestError:
            print "Can't find photo in digikam db. Removed? Digikam: (%s,%s), F-Spot: %s" % (d_album_uri, d_photo_name, f_photo.uri)
            continue

        # Append tag (without checking, I am working on empty tag database)
        print "Adding tag %s to photo %s in album %s" % (d_tag.name, d_photo_name, d_album_uri)
        d_photo.tags.append(d_tag)

############################################################
# The END
############################################################

fspot_session.flush()
digikam_session.flush()

fspot_session.rollback()
digikam_session.commit()
