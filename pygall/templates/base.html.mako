# -*- coding: utf-8 -*-
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <title>${self.title()}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta http-equiv="imagetoolbar" content="false">
    <meta name="description" content="PyGall image gallery based on the Pyramid web framework">
    <meta name="keywords" content="PyGall, image, photo, gallery, Pylons, Pyramid, Galleria">
    <link rel="shortcut icon" type="image/x-icon" href="${request.static_path('pygall:static/app/img/favicon.ico')}" />
${self.stylesheets()}
${self.javascripts()}
</head>

<body>
    <div id="flash"></div>
    <div id="wrapper">
        <div id="header">
            <div style="float:right;">
                <%!
                    from pyramid.security import has_permission
                    from pyramid.url import current_route_url
                %>
                % if has_permission('view', request.context, request):
                <a href="${request.route_path('photos_index', page='', _query=[('debug', 1)]) if debug else request.route_path('photos_index', page='')}">${_('Gallery')}</a> |
                % endif
                % if has_permission('edit', request.context, request):
                <a href="${request.route_path('photos_new', _query=[('debug', 1)]) if debug else request.route_path('photos_new')}">${_('Upload')}</a> |
                <a href="${request.route_path('admin', traverse='')}">${_('Admin')}</a> |
                % endif
                % if logged_in:
                <a href="${request.route_path('logout')}">${_('Logout')} [${logged_in}]</a>
                % else:
                <a href="${request.route_path('login', came_from=current_route_url(request))}">${_('Login')}</a>
                % endif
            </div>
        </div>
        <div id="container">
            ${next.body()}\
        </div>
        <div id="footer">
            <!--FOOTER-->
        </div>
    </div>

</body>
</html>
\
<%def name="title()">${_('PyGall image gallery')}</%def>\
\
<%def name="stylesheets()">\
    % if debug:
    <link href="${request.static_path('pygall:static/app/css/main.css')}" rel="stylesheet" type="text/css" media="screen">
    % else:
    <link href="${request.static_path('pygall:static/build/main.min.css')}" rel="stylesheet" type="text/css" media="screen">
    % endif
</%def>\
\
<%def name="javascripts()">\
    % if request.registry.settings.get('allow_cdn'):
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
    % else:
    <script src="${request.static_path('pygall:static/lib/jquery/jquery-1.6.4.min.js')}"></script>
    % endif
    <script type="text/javascript">
<%include file="globals.js.mako"/>\
    </script>
</%def>\
