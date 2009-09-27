#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import Image
import pyexiv2
from datetime import datetime

from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, Table, Sequence, DateTime, \
        UnicodeText, Integer, String, Unicode, ForeignKey, Boolean
from sqlalchemy.sql import func, join
from sqlalchemy.orm import mapper, sessionmaker, deferred, \
        relation, backref, aliased
from sqlalchemy.exceptions import InvalidRequestError


home = os.environ['HOME']
fspot_db = "sqlite:////home/clemence/.gnome2/f-spot/photos.db" % locals()
pygall_db = "sqlite:////home/bruno/dev/PyGall/development.db" % locals()

photos_src_dir = '/home/data/'
photos_scaled_dest_dir = '/home/bruno/dev/PyGall/pygall/public/'
photos_dest_dir = '/home/bruno/dev/PyGall/pygall/public/data/'
pygall_tag = u'pygall'

ECHO_DB = False
DELETE_ALL_TAGS = False
REBUILD_ONLY_DB = False
REBUILD_ALL = True

quality = 80
dimension = 700

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
           'icon' : deferred(fspot_tags_table.c.icon), # Big: ignore!
           'photos' : relation(FSpotPhoto, secondary = fspot_photo_tags_table),
       })
mapper(FSpotPhoto,
       fspot_photos_table,
       properties = {
           'tags' : relation(FSpotTag, secondary = fspot_photo_tags_table),
       })

############################################################
# PyGall database
############################################################

pygall_engine = create_engine(pygall_db, echo=ECHO_DB)
pygall_metadata = MetaData()

pygall_photos_table = Table(
    "photos", pygall_metadata,
    Column('id', Integer(), Sequence('photos_seq', optional=True),
              primary_key=True),
    Column("uri", Unicode(), nullable=False),
    Column("description", Unicode()),
    Column("rating", Integer()),
    Column("time", DateTime(), nullable=False)
)
# id, uri, description, rating, time

pygall_tags_table = Table(
    "tags", pygall_metadata,
    Column("id", Integer(), primary_key=True),
    Column("name", Unicode(), nullable=False)
)
# id, name, category_id, is_category, sort_priority, icon

pygall_photos_tags_table = Table(
    "photo_tags", pygall_metadata,
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


############################################################
# Connect to the database
############################################################
FSpotSession = sessionmaker(autoflush = True, autocommit = False)
FSpotSession.configure(bind = fspot_engine)
PyGallSession = sessionmaker(autoflush = True, autocommit = False)
PyGallSession.configure(bind = pygall_engine)

fspot_session = FSpotSession()
pygall_session = PyGallSession()
############################################################

# cache dictionnary for tags
pygall_tags = {}

if DELETE_ALL_TAGS or REBUILD_ONLY_DB or REBUILD_ALL:
    pygall_session.execute(pygall_photos_tags_table.delete())
    pygall_session.execute(pygall_tags_table.delete())
if REBUILD_ONLY_DB or REBUILD_ALL:
    pygall_session.execute(pygall_photos_table.delete())

if REBUILD_ALL:
    if os.path.exists(os.path.join(photos_scaled_dest_dir, 'photos')):
        shutil.rmtree(os.path.join(photos_scaled_dest_dir, 'photos'))
    if os.path.exists(os.path.join(photos_dest_dir, 'photos')):
        shutil.rmtree(os.path.join(photos_dest_dir, 'photos'))


def copy_crop_photos(uri):


    src = os.path.join(photos_src_dir, uri)
    dest = os.path.join(photos_dest_dir, uri)
    dest_scaled = os.path.join(photos_scaled_dest_dir, uri)

    exif = pyexiv2.Image(src)
    exif.readMetadata()
    orientation=exif['Exif.Image.Orientation']

    # copy original photo
    if os.path.exists(dest):
        print "Photo already exists (%s): give up..." %dest
    else:
        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)
        shutil.copy2(src, dest)

    # copy scaled photo
    if os.path.exists(dest_scaled):
        print "Scaled photo already exists (%s): give up..." %dest_scaled
    else:
        dirpath = os.path.dirname(dest_scaled)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)

        base, extension = os.path.splitext(src)
        if extension.lower() == ".jpg" or extension.lower() == ".jpeg":
            print "%s" %src
            im = Image.open(src)
            # auto rotate if needed
            if orientation == 6:
                im=im.rotate(270)
            if orientation == 8:
                im=im.rotate(90)

            width_src, height_src = im.size
            if width_src > dimension or height_src > dimension:
                if width_src > height_src:
                    height_dest = dimension * height_src / width_src
                    width_dest = dimension
                else:
                    width_dest = dimension * width_src / height_src
                    height_dest = dimension

                # Si on redimmensionne selon une taille paire, on force la largeur et hauteur 
                # finales de l'image a etre egalement paires.
                if dimension % 2 == 0:
                    height_dest = height_dest - height_dest % 2
                    width_dest = width_dest - width_dest % 2

                im.resize((width_dest, height_dest), Image.ANTIALIAS).save(dest_scaled, quality=quality)
                print "%s" %dest_scaled

            else:
                print "Nothing to do (only copy): photo is to small!"
                shutil.copy(src, dest_scaled)
        else:
            print "Ignoring file %s : only jpg images are allowed!" %src


def fspot_uri_to_pygall(f_uri):
    """
    Takes F-Spot file uri. Returns the relative path
    to be used on PyGall
    """
    if not f_uri.startswith('file://%s' %photos_src_dir):
        raise Exception("Don't know how to handle image %s" % f_uri)
    return f_uri.replace('file://%s' %photos_src_dir, "")

def attach_tag(f_tag, p_photo, force=False):
    if f_tag.name != pygall_tag: # ignore pygall_tag
        if not pygall_tags.has_key(f_tag.name):
            # cache tag from db (or create it if not exist)
            p_tag = pygall_session.query(PyGallTag).filter_by(name = f_tag.name).first()
            if not p_tag:
                print "Creating missing PyGall tag %s" % f_tag.name
                p_tag = PyGallTag(f_tag.name)
                pygall_session.add(p_tag)
                force = True
            pygall_tags[ f_tag.name ] = p_tag

        if force or (pygall_tags[f_tag.name] not in p_photo.tags): # check if already exists
            # append tag to photos_tags
            print "Adding tag %s to photo %s" % (f_tag.name, p_photo.uri)
            p_photo.tags.append(pygall_tags[f_tag.name])


# Iterate on each photo
for f_photo in fspot_session.query(FSpotPhoto).join('tags').filter(FSpotTag.name==pygall_tag).all():
    force_append_tag = False
    # Lookup the same photo in PyGall database
    pygall_uri = fspot_uri_to_pygall(f_photo.uri)
    p_photo = pygall_session.query(PyGallPhoto).filter_by(uri = pygall_uri).first()
    if not p_photo:
        print "Creating missing PyGall photo %s" % pygall_uri
        if not REBUILD_ONLY_DB:
            copy_crop_photos(pygall_uri)
        p_photo = PyGallPhoto(f_photo)
        pygall_session.add(p_photo)
        force_append_tag = True
    for t in f_photo.tags:
        attach_tag(t, p_photo, force_append_tag)



############################################################
# The END
############################################################
fspot_session.flush()
pygall_session.flush()

fspot_session.rollback()
pygall_session.commit()
############################################################

# REMEMBER: Creating missing tags and caching them
# Tricky sqlalchemy request...
#stmt = fspot_session.query(FSpotPhoto).join('tags').filter(FSpotTag.name==pygall_tag).subquery()
#selected_photos_alias = aliased(FSpotPhoto, stmt)
#extracted_tags = fspot_session.query(FSpotTag).join((selected_photos_alias, FSpotTag.photos)).all()

#for f_tag in extracted_tags:
    #p_tag = pygall_session.query(PyGallTag).filter_by(name = f_tag.name).first()
    #if not p_tag:
        #print "Creating missing PyGall tag %s" % f_tag.name
        #p_tag = PyGallTag(f_tag.name)
        #pygall_session.add(p_tag)

    #pygall_tags[ f_tag.name ] = p_tag

