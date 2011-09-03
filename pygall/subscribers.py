import logging
import os

from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.events import subscriber, BeforeRender, NewRequest
from pyramid_formalchemy.events import subscriber as fa_subscriber, \
        IAfterSyncEvent, IBeforeDeleteEvent

from pygall.models import PyGallPhoto
from pygall.lib.imageprocessing import ip, get_info, ORIG

log = logging.getLogger(__name__)

@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event.get('request')
    if request:
        event['_'] = request.translate
        event['localizer'] = request.localizer

tsf = TranslationStringFactory('PyGall')

@subscriber(NewRequest)
def save_locale(event):
    locale = event.request.params.get('_LOCALE_', None)
    if locale:
        event.request.response.set_cookie('_LOCALE_', locale)

@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)
    def auto_translate(string):
        return localizer.translate(tsf(string))
    request.localizer = localizer
    request.translate = auto_translate

@fa_subscriber([PyGallPhoto, IAfterSyncEvent])
def after_photo_sync(context, event):
    if context.time and context.md5sum:
        return
    uri = context.uri
    info = get_info(os.path.join(
        event.request.registry.settings['photos_dir'], ORIG, uri))
    if not context.time:
        context.time = info['date']
        log.debug("context.time = %s" % info['date'])
    if not context.md5sum:
        context.md5sum = info['md5sum']
        log.debug("context.md5sum = %s" % info['md5sum'])

@fa_subscriber([PyGallPhoto, IBeforeDeleteEvent])
def before_photo_delete(context, event):
    ip.remove_image(context.uri)
    log.debug('ip.remove_image(%s)' % context.uri)
