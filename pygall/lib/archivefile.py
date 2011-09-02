import os
import zipfile
import tarfile
import shutil
from types import StringType, UnicodeType


def extractall(archive, dstdir, name='file'):
    """
    extract zip or tar content to dstdir
    archive can be either a filename or a file-like object
    """
    extracted = False
    
    try:
        z = zipfile.ZipFile(archive)
        for name in z.namelist():
            targetname = name
            # directories ends with '/' (on Windows as well)
            if targetname.endswith('/'):
                targetname = targetname[:-1]

            # don't include leading "/" from file name if present
            if targetname.startswith(os.path.sep):
                targetname = os.path.join(dstdir, targetname[1:])
            else:
                targetname = os.path.join(dstdir, targetname)                
            targetname = os.path.normpath(targetname)

            # Create all upper directories if necessary.    
            upperdirs = os.path.dirname(targetname)
            if upperdirs and not os.path.exists(upperdirs):
                os.makedirs(upperdirs)

            # directories ends with '/' (on Windows as well)
            if not name.endswith('/'):
                # copy file
                file(targetname, 'wb').write(z.read(name))
            extracted = True
    except zipfile.BadZipfile:
        pass

    if not extracted:
        archive.seek(0)
        try:
            tar = tarfile.open(name=archive) \
                    if isinstance(archive, (StringType, UnicodeType)) \
                    else tarfile.open(fileobj=archive)
            tar.extractall(path=dstdir)
            extracted = True
        except tarfile.TarError:
            pass

    if not extracted:
        archive.seek(0)
        # seems to be a single file, save it
        if isinstance(archive, (StringType, UnicodeType)):
            shutil.copyfile(
                    archive, os.path.join(dstdir, os.path.basename(archive)))
        else:
            try:
                fdst = open(
                        os.path.join(dstdir, os.path.basename(name)), 'wb')
                shutil.copyfileobj(archive, fdst)
            finally:
                if fdst: fdst.close()

