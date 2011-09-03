# -*- coding: utf-8 -*-
import os
from datetime import datetime
import shutil
import logging
from types import StringType, UnicodeType

import Image
import ExifTags

from pygall.lib.helpers import img_md5, seek, get_size

log = logging.getLogger(__name__)

# CONSTANTS
ORIG = "orig"
SCALED = "scaled"


def get_exif(info):
    ret = {}
    if info == None:
        raise Exception("can't get exif")
    for tag, value in info.items():
        decoded = ExifTags.TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def get_info(img, info=None):
    """
    Get infos about the given image
    """
    if info is None: info = {}
    loc = seek(img, 0)
    im = Image.open(img)
    if 'date' not in info:
        try:
            exif = get_exif(im._getexif())
            info['date'] = datetime.strptime(
                    exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        except:
            info['date'] = None
    if 'md5sum' not in info:
        info['md5sum'] = img_md5(im)
    if 'ext' not in info:
        info['ext'] = im.format.lower()
    if 'size' not in info:
        info['size'] = get_size(img)
    if loc: seek(f, loc)

    return info


class ImageProcessing:
    def __init__(self,
                 dest_dir=None,
                 crop_dimension=700,
                 crop_quality=80):
        self.set_dest_dir(dest_dir)
        self.dimension = crop_dimension
        self.quality = crop_quality

    def set_dest_dir(self, dest_dir):
        if dest_dir is None:
            self.dest_dir = None
            self.abs_orig_dest_dir = None
            self.abs_scaled_dest_dir = None
        else:
            self.dest_dir = dest_dir
            self.abs_orig_dest_dir = os.path.join(self.dest_dir, ORIG)
            self.abs_scaled_dest_dir = os.path.join(self.dest_dir, SCALED)

    def copy_orig(self, src, uri):
        """
        Copy the original image to orig dest directory
        """
        dest = os.path.join(self.abs_orig_dest_dir, uri)

        if not self._check_paths(src, dest):
            return

        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)
        if isinstance(src, (StringType, UnicodeType)):
            shutil.copyfile(src, dest)
        else:
            with open(dest, 'wb') as f:
                loc = seek(src, 0)
                shutil.copyfileobj(src, f)
                src.seek(loc)
        log.info("Copied: %s" % dest)


    def copy_scaled(self, src, uri):
        """
        Rotate and scale image.
        Copy the processed image to scaled dest directory
        """
        dest = os.path.join(self.abs_scaled_dest_dir, uri)

        if not self._check_paths(src, dest):
            return

        loc = seek(src, 0)
        im = Image.open(src)
        try:
            orientation = get_exif(im._getexif())['Orientation']
        except:
            orientation = 0

        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)

        # auto rotate if needed
        if orientation == 6:
            im=im.rotate(270)
        if orientation == 8:
            im=im.rotate(90)

        width_src, height_src = im.size
        if width_src <= self.dimension and height_src <= self.dimension:
            log.info("Scale won't be processed: photo is to small.")
        else:
            if width_src > height_src:
                height_dest = self.dimension * height_src / width_src
                width_dest = self.dimension
            else:
                width_dest = self.dimension * width_src / height_src
                height_dest = self.dimension

            # Si on redimmensionne selon une taille paire, on force la
            # largeur et hauteur finales de l'image a etre egalement
            # paires.
            if self.dimension % 2 == 0:
                height_dest = height_dest - height_dest % 2
                width_dest = width_dest - width_dest % 2

            im=im.resize((width_dest, height_dest), Image.ANTIALIAS)
            log.info("Processed: %s" % dest)

        # save processed image
        im.save(dest, quality=self.quality)
        if loc: seek(src, loc)


    def remove_image(self, uri):
        """
        Remove scaled and orig images associated with the given src image
        """
        # remove scaled image
        dest = os.path.join(self.abs_scaled_dest_dir, uri)
        try:
            os.unlink(dest)
        except:
            pass
        # remove orig image
        dest = os.path.join(self.abs_orig_dest_dir, uri)
        try:
            os.unlink(dest)
        except:
            pass


    def process_image(self, src, md5sum=None):
        """
        Standard processing for the given image:
        Built the destination relative path based on image timestamp
        Copy the original image to orig dest directory
        Copy the scaled and rotated image to scaled dest directory
        Remove the original image from disk
        """
        info = {}
        if md5sum is not None:
            info['md5sum'] = md5sum
        info = get_info(src, info)
        date = info['date'] if info['date'] is not None else datetime.now()
        uri = os.path.join(
            date.strftime("%Y"),
            date.strftime("%m"),
            date.strftime("%d"),
            info['md5sum'] + '.' + info['ext'])
        info['uri'] = uri
        try:
            self.copy_orig(src, uri)
            self.copy_scaled(src, uri)
        except Exception, e:
            # clean up if an exception occured during import
            self.remove_image(uri)
            raise e
        return info


    def _check_paths(self, src, dest=None):
        """
        Checks validity of src and/or dest paths
        """
        # fail if src photo does not exist
        if isinstance(src, (StringType, UnicodeType)) and \
                not os.path.exists(src):
            log.info("Source photo does not exists: %s" % src)
            return False
        # fail if dest photo already exists
        if dest is not None and os.path.exists(dest):
            log.info("Destination photo already exists: %s" % dest)
            return False
        return True


ip = ImageProcessing()
