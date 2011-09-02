# -*- coding: utf-8 -*-
<%inherit file="base.html.mako"/>\
<h3>${_('Upload photos to the PyGall photos gallery')}</h3>
<div id="fileupload">
    <form action="${request.route_path('photos_create')}" method="POST" enctype="multipart/form-data">
        ##{% csrf_token %}
        <div class="fileupload-buttonbar">
            <label class="fileinput-button">
                <span>Add files...</span>
                <input type="file" name="files[]" multiple>
            </label>
            <button type="submit" class="start">Start upload</button>
            <button type="reset" class="cancel">Cancel upload</button>
            <button type="button" class="delete">Delete files</button>
        </div>
    </form>
    <div class="fileupload-content">
        <table class="files"></table>
        <div class="fileupload-progressbar"></div>
    </div>
</div>

<script id="template-upload" type="text/x-jquery-tmpl">
    <tr class="template-upload{{if error}} ui-state-error{{/if}}">
        <td class="preview"></td>
        <td class="name"><%text>${name}</%text></td>
        <td class="size"><%text>${sizef}</%text></td>
        {{if error}}
        <td class="error" colspan="2">Error:
            {{if error === 'maxFileSize'}}File is too big
            {{else error === 'minFileSize'}}File is too small
            {{else error === 'acceptFileTypes'}}Filetype not allowed
            {{else error === 'maxNumberOfFiles'}}Max number of files exceeded
            {{else}}<%text>${error}</%text>
            {{/if}}
        </td>
        {{else}}
        <td class="progress">
            <div></div>
        </td>
        <td class="start">
            <button>Start</button>
        </td>
        {{/if}}
        <td class="cancel">
            <button>Cancel</button>
        </td>
    </tr>
</script>
<script id="template-download" type="text/x-jquery-tmpl">
    <tr class="template-download{{if error}} ui-state-error{{/if}}">
        {{if error}}
        <td></td>
        <td class="name"><%text>${name}</%text></td>
        <td class="size"><%text>${sizef}</%text></td>
        <td class="error" colspan="2">Error:
            {{if error === 1}}File exceeds upload_max_filesize (php.ini directive)
            {{else error === 2}}File exceeds MAX_FILE_SIZE (HTML form directive)
            {{else error === 3}}File was only partially uploaded
            {{else error === 4}}No File was uploaded
            {{else error === 5}}Missing a temporary folder
            {{else error === 6}}Failed to write file to disk
            {{else error === 7}}File upload stopped by extension
            {{else error === 'maxFileSize'}}File is too big
            {{else error === 'minFileSize'}}File is too small
            {{else error === 'acceptFileTypes'}}Filetype not allowed
            {{else error === 'maxNumberOfFiles'}}Max number of files exceeded
            {{else error === 'uploadedBytes'}}Uploaded bytes exceed file size
            {{else error === 'emptyResult'}}Empty file upload result
            {{else}}<%text>${error}</%text>
            {{/if}}
        </td>
        {{else}}
        <td class="preview">
            {{if thumbnail_url}}
            <a href="<%text>${url}</%text>" target="_blank"><img src="<%text>${thumbnail_url}</%text>" style="max-height: 80px; max-width: 80px;"></a>
            {{/if}}
        </td>
        <td class="name">
            <a href="<%text>${url}</%text>" {{if thumbnail_url}}
               target="_blank"{{/if}}><%text>${name}</%text></a>
        </td>
        <td class="size"><%text>${sizef}</%text></td>
        <td colspan="2"></td>
        {{/if}}
        <td class="delete">
            <button data-type="<%text>${delete_type}</%text>" data-url="<%text>${delete_url}</%text>">Delete</button>
        </td>
    </tr>
</script>

##<div id="upload"></div>
\
<%def name="title()">${_('Photos upload')}</%def>\
\
<%def name="stylesheets()">\
    <link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/themes/base/jquery-ui.css" id="theme">
    <link href="${request.static_url('pygall:static/app/css/jquery.fileupload-ui.css')}" rel="stylesheet">
${parent.stylesheets()}
</%def>\
\
<%def name="javascripts()">\
${parent.javascripts()}
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.14/jquery-ui.min.js"></script>
    <script src="http://ajax.aspnetcdn.com/ajax/jquery.templates/beta1/jquery.tmpl.min.js"></script>

    <script src="${request.static_url('pygall:static/app/js/jquery.iframe-transport.js')}"></script>
    <script src="${request.static_url('pygall:static/app/js/jquery.fileupload.js')}"></script>
    <script src="${request.static_url('pygall:static/app/js/jquery.fileupload-ui.js')}"></script>

    <script src="${request.static_url('pygall:static/app/js/App.Upload.js')}" type="text/javascript"></script>
    <script type="text/javascript">
        $(document).ready($.proxy(App.Upload.init, undefined, ${maxfilesize}, ${minfilesize}));
    </script>
</%def>\
\


