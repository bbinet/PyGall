# -*- coding: utf-8 -*-
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <title>${self.title()}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta http-equiv="imagetoolbar" content="false">
    <meta name="description" content="PyGall image gallery based on the Pylons web framework">
    <meta name="keywords" content="PyGall, image, photo, gallery, Pylons, Galleria">
    <link rel="shortcut icon" type="image/x-icon" href="${request.static_url('pygall:static/app/img/favicon.ico')}" />
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
                <a href="${request.route_url('photos_index', page='')}">${_('Gallery')}</a> |
                % endif
                % if has_permission('edit', request.context, request):
                <a href="${request.route_url('photos_new')}">${_('Upload')}</a> |
                % endif
                % if logged_in:
                <a href="${request.route_url('logout')}">${_('Logout')} [${logged_in}]</a>
                % else:
                <a href="${request.route_url('login', came_from=current_route_url(request))}">${_('Login')}</a>
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
    <link href="${request.static_url('pygall:static/app/css/main.css')}" rel="stylesheet" type="text/css" media="screen">
</%def>\
\
<%def name="javascripts()">\
    <script type="text/javascript" src="${request.static_url('pygall:static/app/js/jquery.min.js')}"></script>
    <script type="text/javascript">
<%include file="globals.js.mako"/>\
    </script>
</%def>\
