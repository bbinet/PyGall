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
from pygall.lib.helpers import md5_for_file
from pygall.models import PyGallTag, PyGallPhoto, DBSession, Base
from pygall.models.fspot import \
        Tag as FS_Tag, \
        Photo as FS_Photo, \
        PhotoVersion as FS_PhotoVersion, \
        initialize_sql as FS_initialize_sql, \
        DBSession as FS_DBSession

# globals
IP = None
OPTIONS = None


def get_options(argv):

    def usage():
        print "Usage: %s [options] production.ini" % argv[0]
        print "	--help"
        print "	--drop_db"
        print "	--cleanup_files"
        print "	--src_dir="
        print "	--fspot_db="
        print "	--export_tag="

    try:
        opts, args = getopt.getopt(
                argv[1:],
                "h", [
                    "help",
                    "drop_db",
                    "cleanup_files",
                    "src_dir=",
                    "fspot_db=",
                    "export_tag=", ])
    except getopt.error, msg:
            usage()
            sys.exit(1)

    # set default values for options
    options = {
            "src_dir": os.path.expanduser("~/photos"),
            "fspot_db": os.path.expanduser("~/.config/f-spot/photos.db"),
            "export_tag": u"pygall",
            "drop_db": False,
            "cleanup_files": False,
            }
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("--drop_db", "--cleanup_files"):
            options[opt[2:]] = True
        else:
            options[opt[2:]] = arg

    if len(args) != 1:
        print >>sys.stderr, argv[0] + " should be called with an ini file."
        print >>sys.stderr, "for help use --help"
        sys.exit(1)

    return args, options


def process(row, msgs):
    fspot_id = row.id
    src = decode_fspot_uri(
            row.uri if row.last_version is None else row.last_version.uri)
    with open(src) as f:
        md5sum = md5_for_file(f)

    # copy and scale image if needed
    time, uri = IP.process_image(src, md5sum=md5sum)

    # insert row in db
    photo = PyGallPhoto()
    photo.fspot_id = fspot_id
    photo.uri = uri
    photo.md5sum = md5sum
    photo.description = row.description
    photo.rating = row.rating
    photo.time = time
    try:
        DBSession.add(photo)
        transaction.commit()
        msgs.append("Photo %s has been imported in PyGall" % uri)
    except IntegrityError:
        #print "Photo %s already exists in db" % uri
        transaction.abort()

    return fspot_id


def decode_fspot_uri(uri):
    """
    Takes F-Spot file uri. Returns the relative path to be used on PyGall
    """
    decoded_uri = unquote(uri)
    if not decoded_uri.startswith('file://%s' % OPTIONS['src_dir']):
        raise Exception("Don't know how to handle image %s\n" \
                "Make sure that the --src_dir is valid" % decoded_uri)
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
    FS_initialize_sql(create_engine("sqlite:///%s" % OPTIONS['fspot_db']))

    if OPTIONS['drop_db']:
        Base.metadata.drop_all()
        print "All tables has been dropped"
    Base.metadata.create_all(checkfirst=True)

    if OPTIONS['cleanup_files'] and os.path.exists(settings['photos_dir']):
        print "Photos dir %s has been cleaned up" % settings['photos_dir']
        shutil.rmtree(settings['photos_dir'])
    
    fs_ids = []
    msgs = []
    for row in FS_DBSession.query(FS_Photo).options(
            joinedload('tags', innerjoin=True)).filter(
                    FS_Tag.name==OPTIONS['export_tag']):
        # process the photo and appends fspot_id to the list of processed
        # fspot photos
        fs_ids.append(process(row, msgs))
        sys.stdout.write('.')
        sys.stdout.flush()

    # remove photos coming from fspot that are not associated with tag pygall
    # anymore
    for photo in DBSession.query(PyGallPhoto).filter(and_(
        PyGallPhoto.fspot_id!=None, not_(PyGallPhoto.fspot_id.in_(fs_ids)))):
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
