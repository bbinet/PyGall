# -*- coding: utf-8 -*-
<%inherit file="base.html.mako"/>\
<h3>${_('Upload photos to the PyGall photos gallery')}</h3>
<div id="upload"></div>
\
<%def name="title()">${_('Photos upload')}</%def>\
\
<%def name="stylesheets()">\
    <link rel="stylesheet" type="text/css" href="/gp.fileupload.static/fileupload.css">
${parent.stylesheets()}
</%def>\
\
<%def name="javascripts()">\
${parent.javascripts()}
##    <script src="/gp.fileupload.static/jquery.js" type="text/javascript"></script>
    <script type="text/javascript" src="/gp.fileupload.static/jquery.fileupload.js"></script>
    <script src="${request.static_url('pygall:static/app/js/App.Upload.js')}" type="text/javascript"></script>
    <script type="text/javascript">
        $(document).ready(App.Upload.init);
    </script>
</%def>\
\
