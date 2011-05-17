# -*- coding: utf-8 -*-
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <title>${self.title()}</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta http-equiv="imagetoolbar" content="false">
    <meta name="description" content="PyGall image gallery based on the Pylons web framework">
    <meta name="keywords" content="PyGall, image, photo, gallery, Pylons, Galleria">
${self.stylesheets()}
${self.javascripts()}
</head>

<body>
    <div id="flash"></div>
    <div id="wrapper">
        <div id="header">
            <div style="float:right;">
##                % if h.not_anonymous().is_met(request.environ):
##                    % if h.has_permission('admin').is_met(request.environ):
                    <a href="${request.route_url('photos_index')}">${_('Gallery')}</a> |
                    <a href="${request.route_url('photos_new')}">${_('Upload')}</a> |
##                    % endif
##                    <a href="${url('/account/logout')}">${_('Logout')} [${request.environ['repoze.who.identity']['repoze.who.userid']}]</a>
##                % else:
##                <a href="${url('/account/login', came_from=request.path_url, __logins=0)}">${_('Login')}</a>
##                % endif
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
