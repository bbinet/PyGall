#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import os
import shutil
import subprocess
import Image
import pyexiv2
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Column, \
        Table, Sequence, DateTime, UnicodeText, Integer, \
        String, Unicode, ForeignKey, Boolean, not_
from sqlalchemy.sql import func, join
from sqlalchemy.orm import mapper, sessionmaker, deferred, \
        relation, backref, aliased
from sqlalchemy.exceptions import InvalidRequestError


class ExportGall:
    def __init__(self,
                 src_dir,
                 base_dir,
                 dest_dir,
                 upload_user,
                 upload_host,
                 upload_base_dir,
                 fromdb_url,
                 todb_url,
                 export_tag,
                 verbose=False,
                 rebuild_db=False,
                 cleanup_db=False,
                 cleanup_files=False):
        # default values
        self.src_dir = src_dir
        self.base_dir = base_dir
        self.dest_dir = dest_dir
        self.upload_user = upload_user
        self.upload_host = upload_host
        self.upload_base_dir = upload_base_dir
        self.fromdb_url = fromdb_url
        self.todb_url = todb_url
        self.export_tag = export_tag
        self.verbose = verbose
        self.rebuild_db = rebuild_db
        self.cleanup_db = cleanup_db
        self.cleanup_files = cleanup_files
        self.abs_dest_dir = os.path.join(self.base_dir, self.dest_dir)
        self.upload_base_url = "%s@%s:%s" %(self.upload_user,
                                            self.upload_host,
                                            self.upload_base_dir)
        self.upload_dest_url = os.path.join(self.upload_base_url, self.dest_dir)

    def init_db(self):
        " To be overriden in subclasses "
        pass

    def process(self):
        " To be overriden in subclasses "
        pass

    def upload(self):
        subprocess.check_call(["rsync", "-avz", "--delete", "--force",
                               self.abs_dest_dir, self.upload_dest_url])
        subprocess.check_call(["rsync", "-avz", "--delete", "--force",
                               self.abs_processed_dest_dir, self.upload_processed_dest_url])
        subprocess.check_call(["rsync", "-avz", "--delete", "--force",
                               self.todb_url, self.upload_base_url])



class FSpotToPyGall(ExportGall):
    def __init__(self,
                 src_dir="/home/data/photos/",
                 base_dir="/home/bruno/dev/PyGall/",
                 dest_dir="pygall/public/data/photos/",
                 processed_dest_dir="pygall/public/photos/",
                 upload_user="data",
                 upload_host="srvb",
                 upload_base_dir="/home/data/websites/photos.inneos.org/PyGall/",
                 fromdb_url="/home/clemence/.gnome2/f-spot/photos.db",
                 todb_url="/home/bruno/dev/PyGall/development.db",
                 export_tag="pygall",
                 verbose=False,
                 rebuild_db=False,
                 cleanup_db=False,
                 cleanup_files=False,
                 quality=80,
                 dimension=700):

        ExportGall.__init__(self, src_dir, base_dir, dest_dir, upload_user,
                            upload_host, upload_base_dir, fromdb_url, todb_url,
                            export_tag, verbose, rebuild_db, cleanup_db,
                            cleanup_files)
        self.processed_dest_dir = processed_dest_dir
        self.abs_processed_dest_dir = os.path.join(self.base_dir, self.processed_dest_dir)
        self.upload_processed_dest_url = os.path.join(self.upload_base_url, self.processed_dest_dir)
        self.quality = quality
        self.dimension = dimension

    def init_db(self):
        self._init_fromdb()
        self._init_todb()

    def _fromdb_uri_to_todb(self, uri):
        """
        Takes F-Spot file uri. Returns the relative path
        to be used on PyGall
        """
        if not uri.startswith('file://%s' % self.src_dir):
            raise Exception("Don't know how to handle image %s" % uri)
        return uri.replace('file://%s' % self.src_dir, "")

    def _init_fromdb(self):
        """
        Init FSpot database
        """
        fromdb_engine = create_engine("sqlite:///%s" % self.fromdb_url, echo=self.verbose)
        fromdb_metadata = MetaData()
        
        fromdb_tags_table = Table(
            "tags", fromdb_metadata,
            Column("name", Unicode()),
            autoload = True, autoload_with = fromdb_engine)
        # id, name, category_id, is_category, sort_priority, icon
        
        fromdb_photo_tags_table = Table(
            "photo_tags", fromdb_metadata,
            Column("photo_id", Integer, ForeignKey('photos.id')),
            Column("tag_id", Integer, ForeignKey('tags.id')),
            autoload = True, autoload_with = fromdb_engine)
        # photo_id, tag_id
        
        fromdb_photos_table = Table(
            "photos", fromdb_metadata,
            Column("uri", Unicode()),
            autoload = True, autoload_with = fromdb_engine)
        # id, time, uri, description, roll_id, default_version_id, rating
        
        class FromDbTag(object):
            pass
        class FromDbPhoto(object):
            pass
        
        mapper(FromDbTag,
               fromdb_tags_table,
               properties = {
                   'icon' : deferred(fromdb_tags_table.c.icon), # Big: ignore!
                   'photos' : relation(FromDbPhoto, secondary = fromdb_photo_tags_table),
               })
        mapper(FromDbPhoto,
               fromdb_photos_table,
               properties = {
                   'tags' : relation(FromDbTag, secondary = fromdb_photo_tags_table),
               })

        FSpotSession = sessionmaker(autoflush = True, autocommit = False)
        FSpotSession.configure(bind = fromdb_engine)

        self.FromDbMain = FromDbPhoto
        self.FromDbTag = FromDbTag
        self.fromdb_session = FSpotSession()

        
    def _init_todb(self):
        """
        Init PyGall database
        """
        todb_engine = create_engine("sqlite:///%s" % self.todb_url, echo=self.verbose)
        todb_metadata = MetaData()
        
        todb_photos_table = Table(
            "photos", todb_metadata,
            Column('id', Integer(), Sequence('photos_seq', optional=True),
                      primary_key=True),
            Column("uri", Unicode(), nullable=False, index=True),
            Column("description", Unicode()),
            Column("rating", Integer()),
            Column("time", DateTime(), nullable=False)
        )
        # id, uri, description, rating, time
        
        todb_tags_table = Table(
            "tags", todb_metadata,
            Column("id", Integer(), primary_key=True),
            Column("name", Unicode(), nullable=False)
        )
        # id, name, category_id, is_category, sort_priority, icon
        
        todb_photos_tags_table = Table(
            "photo_tags", todb_metadata,
            Column("photo_id", Integer, ForeignKey('photos.id')),
            Column("tag_id", Integer, ForeignKey('tags.id'))
        )
        # photo_id, tag_id
        
        class ToDbTag(object):
            def __init__(self, name):
                self.name = name
        
        class ToDbPhoto(object):
            def __init__(self, uri="", description="", rating=-1, time=datetime(1,1,1)):
                self.uri = uri
                self.description = description
                self.rating = rating
                self.time = time
        
        mapper(ToDbTag,
               todb_tags_table,
               properties = {
                   'photos' : relation(ToDbPhoto, secondary = todb_photos_tags_table),
                })
        
        mapper(ToDbPhoto,
               todb_photos_table,
               properties = {
                  'tags' : relation(ToDbTag, secondary = todb_photos_tags_table),
               })

        ToDbSession = sessionmaker(autoflush = True, autocommit = False)
        ToDbSession.configure(bind = todb_engine)

        self.ToDbMain = ToDbPhoto
        self.ToDbTag = ToDbTag
        self.todb_session = ToDbSession()
        self.sqla_tables = [todb_photos_table, todb_tags_table, todb_photos_table]

        if self.rebuild_db:
            # remove and recreate db
            os.remove(self.todb_url)
            todb_metadata.create_all(bind=todb_engine)


    def process(self):
        # cleanup if wanted
        if self.cleanup_db:
            for table in self.sqla_tables:
                self.todb_session.execute(table.delete())
        if self.cleanup_files:
            if os.path.exists(self.abs_processed_dest_dir):
                print "Cleaning directory %s..." % self.abs_processed_dest_dir
                shutil.rmtree(self.abs_processed_dest_dir)
            if os.path.exists(self.abs_dest_dir):
                print "Cleaning directory %s..." % self.abs_dest_dir
                shutil.rmtree(self.abs_dest_dir)

        (full_list, simple_list) = self._get_export_list()
        self._process_db(full_list, simple_list)
        self._process_files(simple_list)

    def _get_export_list(self):
        full_list = []
        simple_list = []
        q = self.fromdb_session.query(self.FromDbMain).join('tags').filter(self.FromDbTag.name==self.export_tag)
        for row in q.all():
            full_list.append({
                "uri": self._fromdb_uri_to_todb(row.uri),
                "description": row.description,
                "rating": row.rating,
                "time": datetime.fromtimestamp(row.time),
                "tags": [tag.name for tag in row.tags]
            })
            simple_list.append(self._fromdb_uri_to_todb(row.uri))
        return (full_list, simple_list)

    def _process_db(self, full_list, simple_list):
        cache_tags = {}
        def _process_tags(row, tags):
            # remove old tags
            for dbtag in row.tags:
                if dbtag.name not in tags:
                    row.tags.remove(dbtag)
                    print "[db] Disassociated : tag %s to photo %s" % (dbtag.name, row.uri)
            # add new tags
            for tag in tags:
                if tag != self.export_tag: # ignore export_tag
                    new_tag = False
                    if not cache_tags.has_key(tag):
                        # cache tag from db (or create it if not exist)
                        dbtag = self.todb_session.query(self.ToDbTag).filter_by(name=tag).first()
                        if not dbtag:
                            new_tag = True
                            print "[db] Created : tag %s" % tag
                            dbtag = self.ToDbTag(tag)
                            self.todb_session.add(dbtag)
                        cache_tags[tag] = dbtag

                    if new_tag or (cache_tags[tag] not in row.tags):
                        # append tag if not already exists
                        row.tags.append(cache_tags[tag])
                        print "[db] Associated : tag %s to photo %s" % (tag, row.uri)

        # remove old photos
        count = self.todb_session.query(self.ToDbMain).filter(not_(self.ToDbMain.uri.in_(simple_list))).delete()
        if count > 0:
            print "[db] Removed : %d photo(s)" % count

        # add new photos
        for item in full_list:
            # look for the same photo in ToDb
            row = self.todb_session.query(self.ToDbMain).filter_by(uri=item["uri"]).first()
            if not row:
                row = self.ToDbMain(item["uri"], item["description"], item["rating"], item["time"])
                self.todb_session.add(row)
                print "[db] Created : photo %s" % item["uri"]
            _process_tags(row, item["tags"])

        # end db sessions
        self.fromdb_session.flush()
        self.todb_session.flush()
        self.fromdb_session.rollback()
        self.todb_session.commit()


    def _process_files(self, list):
        # remove old processed files
        original_files = []
        processed_files = []
        for uri in list:
            original_files.append(os.path.join(self.abs_dest_dir, uri))
            processed_files.append(os.path.join(self.abs_processed_dest_dir, uri))
        
        # walk in abs_dest_dir and abs_processed_dest_dir and remove all files not in 'list'
        for root, dirs, files in os.walk(self.abs_dest_dir):
            for file in files:
                f = os.path.join(root, file)
                if f not in original_files:
                    print "Removed : %s" % f
                    os.remove(f)
        for root, dirs, files in os.walk(self.abs_processed_dest_dir):
            for file in files:
                f = os.path.join(root, file)
                if f not in processed_files:
                    print "Removed : %s (processed)" % f
                    os.remove(f)

        # add missing files
        for uri in list:
            src = os.path.join(self.src_dir, uri)
            dest = os.path.join(self.abs_dest_dir, uri)

            # copy original photo
            if os.path.exists(dest):
                if self.verbose:
                    print "Photo already exists (%s): give up..." % dest
            else:
                dirpath = os.path.dirname(dest)
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath, 0755)
                shutil.copy2(src, dest)
                print "Copied : %s" % dest

            # copy scaled photo
            dest_processed = os.path.join(self.abs_processed_dest_dir, uri)
            exif = pyexiv2.Image(src)
            exif.readMetadata()
            orientation=exif['Exif.Image.Orientation']

            if os.path.exists(dest_processed):
                if self.verbose:
                    print "Processed photo already exists (%s): give up..." % dest_processed
            else:
                dirpath = os.path.dirname(dest_processed)
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath, 0755)

                base, extension = os.path.splitext(src)
                if extension.lower() == ".jpg" or extension.lower() == ".jpeg":
                    im = Image.open(src)
                    # auto rotate if needed
                    if orientation == 6:
                        im=im.rotate(270)
                    if orientation == 8:
                        im=im.rotate(90)

                    width_src, height_src = im.size
                    if width_src > self.dimension or height_src > self.dimension:
                        if width_src > height_src:
                            height_dest = self.dimension * height_src / width_src
                            width_dest = self.dimension
                        else:
                            width_dest = self.dimension * width_src / height_src
                            height_dest = self.dimension

                        # Si on redimmensionne selon une taille paire, on force la largeur et hauteur 
                        # finales de l'image a etre egalement paires.
                        if self.dimension % 2 == 0:
                            height_dest = height_dest - height_dest % 2
                            width_dest = width_dest - width_dest % 2

                        im.resize((width_dest, height_dest), Image.ANTIALIAS).save(dest_processed, quality=self.quality)
                        print "Processed : %s" % dest_processed

                    else:
                        print "Nothing to do (only copy): photo is to small!"
                        shutil.copy(src, dest_processed)
                else:
                    print "Ignored : %s is not jpg!" %src


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def help(name):
    print >>sys.stdout, "Usage: %s [options]" % name
    print >>sys.stdout, "	--help"
    print >>sys.stdout, "	--verbose"
    print >>sys.stdout, "	--rebuild_db"
    print >>sys.stdout, "	--cleanup_db"
    print >>sys.stdout, "	--cleanup_files"
    print >>sys.stdout, "	--src_dir="
    print >>sys.stdout, "	--base_dir="
    print >>sys.stdout, "	--dest_dir="
    print >>sys.stdout, "	--processed_dest_dir="
    print >>sys.stdout, "	--upload_user="
    print >>sys.stdout, "	--upload_host="
    print >>sys.stdout, "	--upload_base_dir="
    print >>sys.stdout, "	--fromdb_url="
    print >>sys.stdout, "	--todb_url="
    print >>sys.stdout, "	--export_tag="
    print >>sys.stdout, "	--quality="
    print >>sys.stdout, "	--dimension="


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(
                argv[1:],
                "h",
                ["help",
                 "verbose",
                 "rebuild_db",
                 "cleanup_db",
                 "cleanup_files",
                 "src_dir=",
                 "base_dir=",
                 "dest_dir=",
                 "processed_dest_dir=",
                 "upload_user=",
                 "upload_host=",
                 "upload_base_dir=",
                 "fromdb_url=",
                 "todb_url=",
                 "export_tag=",
                 "quality=",
                 "dimension="]
            )
            options = {}
            for opt, arg in opts:
                if opt in ("-h", "--help"):
                    help(argv[0])
                    return 0
                elif opt in ("--verbose", "--rebuild_db", "--cleanup_db", "--cleanup_files"):
                    options[opt[2:]] = True
                else:
                    options[opt[2:]] = arg

            export = FSpotToPyGall(**options)
            export.init_db()
            export.process()
            export.upload()
            return 0
        except getopt.error, msg:
             raise Usage(msg)
        # more code, unchanged
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())

