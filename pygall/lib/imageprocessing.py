# -*- coding: utf-8 -*-
import os
import datetime
import shutil
import Image
import pyexiv2
import logging

log = logging.getLogger(__name__)

# CONSTANTS
ORIG = "orig"
SCALED = "scaled"

class ImageProcessing:

    def __init__(self,
                 dest_dir,
                 crop_dimension=700,
                 crop_quality=80):
        self.dest_dir = dest_dir
        self.abs_orig_dest_dir = os.path.join(self.dest_dir, ORIG)
        self.abs_scaled_dest_dir = os.path.join(self.dest_dir, SCALED)
        self.dimension = crop_dimension
        self.quality = crop_quality


    def copy_orig(self, src, dest_uri):
        """
        Copy the original image to orig dest directory
        """
        dest = os.path.join(self.abs_orig_dest_dir, dest_uri)

        self._check_paths(src, dest)

        # copy original photo
        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)
        shutil.copy2(src, dest)
        log.info("Copied: %s" % dest)


    def copy_scaled(self, src, dest_uri):
        """
        Rotate and scale image.
        Copy the processed image to scaled dest directory
        """
        dest = os.path.join(self.abs_scaled_dest_dir, dest_uri)

        self._check_paths(src, dest)

        # copy scaled and rotated photo
        exif = pyexiv2.Image(src)
        try:
            exif.readMetadata()
            orientation=exif['Exif.Image.Orientation']
        except:
            orientation=0

        dirpath = os.path.dirname(dest)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, 0755)

        im = Image.open(src)
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


    def unlink(self, src):
        """
        Remove the original image from disk
        """

        self._check_paths(src)

        # unlink original photo
        os.unlink(src)
        log.info("Removed: %s" % src)


    def process_image(self, src):
        """
        Standard processing for the given image:
        Built the destination relative path based on image timestamp
        Copy the original image to orig dest directory
        Copy the scaled and rotated image to scaled dest directory
        Remove the original image from disk
        """
        date = self._get_datetime(src)
        dest_uri = os.path.join(
            date.strftime("%Y"),
            date.strftime("%m"),
            date.strftime("%d"),
            os.path.basename(src))
        self.copy_orig(src, dest_uri)
        self.copy_scaled(src, dest_uri)
        self.unlink(src)
        return (date, dest_uri)


    def _get_datetime(self, src):
        """
        Built the destination relative path based on image timestamp
        """
        self._check_paths(src)

        exif = pyexiv2.Image(src)
        try:
            exif.readMetadata()
            date = exif['Exif.Image.DateTime']
        except:
            # TODO: return None and handle this at a higher level
            date = datetime.datetime.today()

        return date


    def _check_paths(self, src, dest=None):
        """
        Checks validity of src and/or dest paths
        """
        # abort if src photo does not exist
        if not os.path.exists(src):
            raise Exception("Source photo does not exists")

        # abort if src photo is not jpeg
        base, extension = os.path.splitext(src)
        if extension.lower() != ".jpg" and extension.lower() != ".jpeg":
            raise Exception("Source photo is not jpg")

        # abort if dest photo already exists
        if dest is not None and os.path.exists(dest):
            raise Exception("Destination photo already exists")

