import os, zipfile, tarfile, shutil

def extractall(archive, dstdir):
    """ extract zip or tar content to dstdir"""
    
    if zipfile.is_zipfile(archive):
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

    elif tarfile.is_tarfile(archive):
        tar = tarfile.open(archive)
        tar.extractall(path=dstdir)

    else:
        # seems to be a single file, save it
        shutil.copyfile(archive, os.path.join(dstdir, os.path.basename(archive)))

