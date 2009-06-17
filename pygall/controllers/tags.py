import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from pygall.lib.base import BaseController, render
from pygall.model.meta import Session
from pygall.model import FSpotTag

log = logging.getLogger(__name__)

class TagsController(BaseController):

    def index(self):
        tags = Session.query(FSpotTag)
        serialized_tags = []
        for tag in tags:
            serialized_tags.append(tag.name);
        return str(serialized_tags)
