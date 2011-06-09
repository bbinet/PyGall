# -*- coding: utf-8 -*-
<%inherit file="base.html.mako"/>\
<div id="side-a">
    <h1>${_('PyGall photo gallery!')}</h1>
    <ul class="gallery_demo">
        <% first=True %>
        % for photo in photos:
        % if first:
        <li title="${photo.time.strftime('%d/%m/%Y')}" class="active">
        <% first=False %>
        % else:
        <li title="${photo.time.strftime('%d/%m/%Y')}">
        % endif
            <img src="${request.route_url('photos/',subpath='/scaled/'+str(photo.uri))}" alt="${photo.uri}" title="${photo.description or ''}">
        </li>
        % endfor
    </ul>
    <div class="nav">
        <p>
            <a href="#" onclick="$.galleria.prev(); return false;">&laquo; ${_('previous')}</a> | <a href="#" onclick="$.galleria.next(); return false;">${_('next')} &raquo;</a>
        </p>
        <p>
            % if edit:
            ${photos.pager(_('Page') + ': $link_previous ~4~ $link_next', edit=edit)}
            % else:
            ${photos.pager(_('Page') + ': $link_previous ~4~ $link_next')}
            % endif
        </p>
    </div>

</div>

<div id="side-b">
    <!--image box-->
</div>
\
<%def name="stylesheets()">\
    <link href="${request.static_url('pygall:static/app/css/galleria.css')}" rel="stylesheet" type="text/css" media="screen">
${parent.stylesheets()}
</%def>\
\
<%def name="javascripts()">\
${parent.javascripts()}
    <script type="text/javascript" src="${request.static_url('pygall:static/app/js/jquery.galleria.js')}"></script>
    <script type="text/javascript" src="${request.static_url('pygall:static/app/js/App.Galleria.js')}"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            App.edit = ${"true" if edit else "false"};
            App.Galleria.init();
        });
    </script>
</%def>\
