# -*- coding: utf-8 -*-
<%inherit file="base.html.mako"/>\
<h1>${_('PyGall photo gallery!')}</h1>
<div id="galleria">
    % for photo in photos:
    <img src="${request.static_path(photos_dir+'/scaled/'+str(photo.uri))}" alt="${photo.description or ''}" title="${photo.time.strftime('%d/%m/%Y') if photo.time else ''}">
    % endfor
</div>
<div id="pager-nav">
    ${photos.pager(_('Page') + ': $link_previous ~4~ $link_next')}
</div>
\
\
<%def name="stylesheets()">\
${parent.stylesheets()}
</%def>\
\
<%def name="javascripts()">\
${parent.javascripts()}
    <script type="text/javascript" src="${request.static_url('pygall:static/lib/galleria/src/galleria.js')}"></script>
    <script type="text/javascript" src="${request.static_url('pygall:static/lib/galleria/src/plugins/history/galleria.history.js')}"></script>
    <script type="text/javascript" src="${request.static_url('pygall:static/lib/galleria/src/themes/classic/galleria.classic.js')}"></script>
    ##<script type="text/javascript" src="${request.static_url('pygall:static/lib/galleria/src/themes/folio/galleria.folio.min.js')}"></script>
    <script>
        $(document).ready(function() {
            $('#galleria').galleria({
                height:600
            });
        });
    </script>
</%def>\
