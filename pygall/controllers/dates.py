import logging
from datetime import datetime

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import FSpotPhoto

log = logging.getLogger(__name__)

class DatesController(BaseController):

    def index(self):
        photos = Session.query(FSpotPhoto)
        serialized_photos = []
        for photo in photos:
            photo_date = datetime.fromtimestamp(photo.time)
            serialized_photos.append(photo_date.ctime());
        return str(serialized_photos)
