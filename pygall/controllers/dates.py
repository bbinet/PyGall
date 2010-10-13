# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from sqlalchemy import extract, func
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import PyGallPhoto

log = logging.getLogger(__name__)

class DatesController(BaseController):

    @ActionProtector(not_anonymous())
    def index(self):
        photos = Session.query(
            extract('year', PyGallPhoto.time).label('year'), func.count('*').label('value')
        ).group_by('year')
        serialized_photos = []
        for photo in photos:
            serialized_photos.append(u"Année %d: %d photos" %photo);
        response.charset = 'utf8'
        response.content_type = 'text/plain' 
        return '\n'.join(serialized_photos)
