import logging

from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.events import subscriber, BeforeRender, NewRequest
from pyramid_formalchemy.events import subscriber as fa_subscriber, \
        IBeforeValidateEvent, IBeforeDeleteEvent

from pygall.models import PyGallPhoto
from pygall.lib.imageprocessing import ip

log = logging.getLogger(__name__)

@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event.get('request')
    if request:
        event['_'] = request.translate
        event['localizer'] = request.localizer

tsf = TranslationStringFactory('PyGall')

@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)
    def auto_translate(string):
        return localizer.translate(tsf(string))
    request.localizer = localizer
    request.translate = auto_translate

    @fa_subscriber([PyGallPhoto, IBeforeValidateEvent])
    def before_photo_validate(context, event):
        print "%r will be validated" % context
        # TODO: set date and md5sum if not already set (and remove ugly hack)

    @fa_subscriber([PyGallPhoto, IBeforeDeleteEvent])
    def before_photo_delete(context, event):
        ip.remove_image(context.uri)
        log.debug('ip.remove_image(%s)' % context.uri)
