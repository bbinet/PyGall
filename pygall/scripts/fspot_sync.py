"""Sync the database and photos directory with f-spot

Run this every time you want to synchronize with f-spot::

    python -m pygall.scripts.fspot_sync [options] development.ini
"""
import sys
import os
import shutil
import getopt
from datetime import datetime
from urllib import unquote

from pyramid.paster import get_app
from sqlalchemy import create_engine, and_, not_
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import transaction

from pygall.lib.imageprocessing import ImageProcessing
from pygall.lib.helpers import img_md5
from pygall.models import Tag, Photo, DBSession, Base
from pygall.models.fspot import \
        Tag as FS_Tag, \
        Photo as FS_Photo, \
        PhotoVersion as FS_PhotoVersion, \
        initialize_sql as FS_initialize_sql, \
        DBSession as FS_DBSession

# globals
IP = None
OPTIONS = None
TAGS = None


def get_options(argv):

    def usage():
        print "Usage: %s [options] production.ini" % argv[0]
        print " --help"
        print "     prints this usage message"
        print " --drop-db"
        print "     drop the pygall database which will then be repopulated"
        print "     with photos imported from F-spot"
        print " --cleanup-files"
        print "     cleanup all existing photos in PyGall before importing new"
        print "     photos from F-spot"
        print " --skip-existing"
        print "     don't try to update metadata for photos that already exist"
        print "     in PyGall database"
        print " --fspot-photosdir=[~/Photos]"
        print "     specifiy the path to F-spot photos directory"
        print " --fspot-db=[~/.config/f-spot/photos.db]"
        print "     specifiy the path to F-spot database"
        print " --fspot-exporttag=[pygall]"
        print "     specifiy the tag which determines which photos are imported"
        print "     from F-spot"

    try:
        opts, args = getopt.getopt(
                argv[1:],
                "h", [
                    "help",
                    "drop-db",
                    "cleanup-files",
                    "skip-existing",
                    "fspot-photosdir=",
                    "fspot-db=",
                    "fspot-exporttag=", ])
    except getopt.error, msg:
            usage()
            sys.exit(1)

    # set default values for options
    options = {
            "fspot-photosdir": os.path.expanduser("~/Photos"),
            "fspot-db": os.path.expanduser("~/.config/f-spot/photos.db"),
            "fspot-exporttag": u"pygall",
            "drop-db": False,
            "cleanup-files": False,
            "skip-existing": False,
            }
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("--drop-db", "--cleanup-files", "--skip-existing"):
            options[opt[2:]] = True
        else:
            options[opt[2:]] = arg

    if len(args) != 1:
        print >>sys.stderr, argv[0] + " should be called with an ini file."
        print >>sys.stderr, "for help use --help"
        sys.exit(1)

    return args, options


def get_tags(tags):
    global TAGS
    if TAGS is None:
        TAGS = {}
        for t in DBSession.query(Tag):
            TAGS[t.name] = t
    res = []
    for tname in tags:
        if tname not in TAGS:
            TAGS[tname] = Tag(tname)
            DBSession.add(TAGS[tname])
        res.append(DBSession.merge(TAGS[tname]))
    return res


def process(row, msgs):
    fspot_id = row.id
    insert = False
    photo = DBSession.query(Photo).filter_by(fspot_id=fspot_id).first()
    if photo is None:
        insert = True
        photo = Photo()
        src = decode_fspot_uri(
                row.uri if row.last_version is None else row.last_version.uri)
        md5sum = img_md5(src)
        # copy and scale image if needed
        info = IP.process_image(src, md5sum=md5sum)
        # set photo db record
        photo.fspot_id = fspot_id
        photo.uri = info['uri']
        photo.md5sum = md5sum
        photo.time = info['date']

    if insert or not OPTIONS['skip-existing']:
        # update row in db
        if row.description:
            photo.description = row.description
        photo.rating = row.rating
        photo.tags = get_tags([t.name for t in row.tags])

    #TODO: detect if photo version has changed and update photo accordingly

    try:
        uri = photo.uri # keep track of photo.uri outside the DBSession
        DBSession.add(photo)
        transaction.commit()
        if insert:
            msgs.append("Photo %s has been imported in PyGall" % uri)
    except IntegrityError:
        #print "Photo %s already exists in db" % uri
        transaction.abort()
        #TODO: make it possible to update record

    return fspot_id


def decode_fspot_uri(uri):
    decoded_uri = unquote(uri)
    if not decoded_uri.startswith('file://%s' % OPTIONS['fspot-photosdir']):
        raise Exception("Don't know how to handle image %s\n" \
                "Make sure that the --fspot-photosdir is valid" % decoded_uri)
    return decoded_uri.replace('file://', '')


def main():
    global IP, OPTIONS
    args, OPTIONS = get_options(sys.argv)

    ini_file = args[0]
    app = get_app(ini_file, "PyGall")
    settings = app.registry.settings
    OPTIONS['photos_dir'] = settings['photos_dir']
    IP = ImageProcessing(settings['photos_dir'])

    # configure engine for fspot database
    FS_initialize_sql(create_engine("sqlite:///%s" % OPTIONS['fspot-db']))

    if OPTIONS['drop-db']:
        Base.metadata.drop_all()
        print "All tables has been dropped"
    Base.metadata.create_all(checkfirst=True)

    if OPTIONS['cleanup-files'] and os.path.exists(settings['photos_dir']):
        print "Photos dir %s has been cleaned up" % settings['photos_dir']
        shutil.rmtree(settings['photos_dir'])
    
    fs_ids = []
    msgs = []
    for row in FS_DBSession.query(FS_Tag)\
            .filter_by(name=OPTIONS['fspot-exporttag']).one().photos:
        # process the photo and appends fspot_id to the list of processed
        # fspot photos
        fs_ids.append(process(row, msgs))
        sys.stdout.write('.')
        sys.stdout.flush()

    # remove photos coming from fspot that are not associated with tag pygall
    # anymore
    for photo in DBSession.query(Photo).filter(and_(
        Photo.fspot_id!=None, not_(Photo.fspot_id.in_(fs_ids)))).all():
        IP.remove_image(photo.uri)
        DBSession.delete(photo)
        transaction.commit()
        msgs.append("Photo %s has been deleted from PyGall" % photo.uri)
        sys.stdout.write('.')
        sys.stdout.flush()

    print ''
    if len(msgs) > 0:
        for msg in msgs:
            print msg
    else:
        print "Nothing to do..."


if __name__ == "__main__":
    main()
