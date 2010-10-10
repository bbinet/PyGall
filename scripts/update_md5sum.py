# Execute this script in paster shell to update the md5sum of all photos

import os
from pygall.model.meta import Session
from pygall.model import PyGallPhoto
from pygall.lib.helpers import md5_for_file

for p in Session.query(PyGallPhoto):
    path = os.path.join('./pygall/public/data/photos/orig', p.uri)
    if os.path.exists(path):
        f = open(path)
        p.md5sum = md5_for_file(f)
        f.close()
        Session.commit()
