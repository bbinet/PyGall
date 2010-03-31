# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import PyGallTag

log = logging.getLogger(__name__)

class TagsController(BaseController):

    def index(self):
        tags = Session.query(PyGallTag)
        serialized_tags = []
        for tag in tags:
            serialized_tags.append(tag.name);
        response.charset = 'utf8'
        response.content_type = 'text/plain' 
        return '\n'.join(serialized_tags)
