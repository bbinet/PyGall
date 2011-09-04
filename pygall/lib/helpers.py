"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
import os
import errno
import hashlib
from types import StringType, UnicodeType
from cStringIO import StringIO

from ImageFile import ImageFile
import Image


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def seek(f, offset, whence=0):
    loc = None
    if not isinstance(f, (StringType, UnicodeType)):
        loc = f.tell()
        f.seek(offset, whence)
    return loc

def get_size(f):
    """
    get the size of a file
    param can be either a filename or a file-like object
    """
    if isinstance(f, (StringType, UnicodeType)):
        size = os.path.getsize(f)
    else:
        pos = seek(f, 0, os.SEEK_END)
        size = f.tell()
        seek(f, pos)
    return size

def img_md5(f, block_size=2**20):
    # use PIL image to ignore exif tags when calculating md5sum
    md5 = hashlib.md5()
    buf = None
    if isinstance(f, ImageFile):
        buf = StringIO(f.tostring())
    else:
        loc = seek(f, 0)
        buf = StringIO(Image.open(f).tostring())
        if loc: seek(f, loc)
    while True:
        data = buf.read(block_size)
        if not data:
            break
        md5.update(data)
    return unicode(md5.hexdigest())

def unchroot_path(path, chroot):
    if not isinstance(path, (StringType, UnicodeType)):
        raise Exception('Bad path (type is not string)')
    while path.startswith(os.sep):
        path = path[len(os.sep):]
    if not path.startswith(os.path.basename(chroot)):
        raise Exception('Bad path (no chroot prefix)')

    uri = os.path.normpath(path[len(os.path.basename(chroot)):])
    while uri.startswith(os.sep):
        uri = uri[len(os.sep):]
    unchrooted = os.path.normpath(os.path.join(chroot, uri))

    if not unchrooted.startswith(chroot):
        raise Exception('Bad path (chroot protected)')
    if not os.path.exists(unchrooted):
        raise Exception('Bad path (does not exist): %s' %unchrooted)

    return (unchrooted, uri)

def remove_empty_dirs(root, uri=None):
    if uri:
        while uri != os.path.dirname(uri):
            uri = os.path.dirname(uri)
            try:
                os.rmdir(os.path.join(root, uri))
            except OSError:
                break
    else:
        # remove empty directories
        for dirpath, dirs, files in os.walk(root, topdown=False):
            for subdirname in dirs:
                try:
                    os.rmdir(os.path.join(dirpath, subdirname))
                except OSError:
                    pass


def main(argv):
    for arg in argv[1:]:
        print "img_md5('%s') --> %s" % (arg, img_md5(arg))

if __name__ == "__main__":
    import sys
    main(sys.argv)
