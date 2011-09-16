# -*- coding: utf-8 -*-
<%inherit file="base.html.mako"/>\
<h1>${_('Upload photos to the PyGall photos gallery')}</h1>
<div id="fileupload">
    <form action="${request.route_path('photos_create')}" method="POST" enctype="multipart/form-data">
        <div class="fileupload-buttonbar">
            <label class="fileinput-button">
                <span>${_('Add files...')}</span>
                <input type="file" name="files[]" multiple>
            </label>
            <button type="submit" class="start">${_('Start upload')}</button>
            <button type="reset" class="cancel">${_('Cancel upload')}</button>
            <button type="button" class="delete">${_('Delete files')}</button>
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
        <td class="error" colspan="2">${_('Error:')}
            {{if error === 'maxFileSize'}}${_('File is too big')}
            {{else error === 'minFileSize'}}${_('File is too small')}
            {{else error === 'acceptFileTypes'}}${_('Filetype not allowed')}
            {{else error === 'maxNumberOfFiles'}}${_('Max number of files exceeded')}
            {{else}}<%text>${error}</%text>
            {{/if}}
        </td>
        {{else}}
        <td class="progress">
            <div></div>
        </td>
        <td class="start">
            <button>${_('Start')}</button>
        </td>
        {{/if}}
        <td class="cancel">
            <button>${_('Cancel')}</button>
        </td>
    </tr>
</script>
<script id="template-download" type="text/x-jquery-tmpl">
    <tr class="template-download{{if error}} ui-state-error{{/if}}">
        {{if error}}
        <td class="preview">
            {{if url}}<a href="<%text>${url}</%text>" target="_blank">
            {{if thumbnail_url}}<img src="<%text>${thumbnail_url}</%text>" style="max-height: 80px; max-width: 80px;">{{else}}${_('Show image')}{{/if}}
            </a>{{/if}}
        </td>
        <td class="name"><%text>${name}</%text></td>
        <td class="size"><%text>${sizef}</%text></td>
        <td class="error" colspan="2">${_('Error:')}
            {{if error === 1}}${_('File exceeds upload_max_filesize (php.ini directive)')}
            {{else error === 2}}${_('File exceeds MAX_FILE_SIZE (HTML form directive)')}
            {{else error === 3}}${_('File was only partially uploaded')}
            {{else error === 4}}${_('No File was uploaded')}
            {{else error === 5}}${_('Missing a temporary folder')}
            {{else error === 6}}${_('Failed to write file to disk')}
            {{else error === 7}}${_('File upload stopped by extension')}
            {{else error === 'maxFileSize'}}${_('File is too big')}
            {{else error === 'minFileSize'}}${_('File is too small')}
            {{else error === 'acceptFileTypes'}}${_('Filetype not allowed')}
            {{else error === 'maxNumberOfFiles'}}${_('Max number of files exceeded')}
            {{else error === 'uploadedBytes'}}${_('Uploaded bytes exceed file size')}
            {{else error === 'emptyResult'}}${_('Empty file upload result')}
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
            <button data-type="<%text>${delete_type}</%text>" data-url="<%text>${delete_url}</%text>">${_('Delete')}</button>
        </td>
    </tr>
</script>

\
<%def name="title()">${_('Photos upload')}</%def>\
\
<%def name="stylesheets()">\
    % if request.registry.settings.get('allow_cdn'):
    <link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/dark-hive/jquery-ui.css" id="theme">
    % else:
    <link rel="stylesheet" href="${request.static_path('pygall:static/lib/jquery-ui/jquery-ui-dark-hive-1.8.16.css')}" id="theme">
    % endif
    % if debug:
    <link href="${request.static_path('pygall:static/app/css/jquery.fileupload-ui.css')}" rel="stylesheet">
    % else:
    <link href="${request.static_path('pygall:static/build/jquery.fileupload-ui.min.css')}" rel="stylesheet">
    % endif
${parent.stylesheets()}
</%def>\
\
<%def name="javascripts()">\
${parent.javascripts()}
% if debug:
    <script src="${request.static_path('pygall:static/lib/jquery-ui/jquery-ui-1.8.16.js')}"></script>
    <script src="${request.static_path('pygall:static/lib/jquery-tmpl/jquery-tmpl-beta1.js')}"></script>
    <script src="${request.static_path('pygall:static/app/js/jquery.iframe-transport.js')}"></script>
    <script src="${request.static_path('pygall:static/app/js/jquery.fileupload.js')}"></script>
    <script src="${request.static_path('pygall:static/app/js/jquery.fileupload-ui.js')}"></script>
    <script src="${request.static_path('pygall:static/app/js/App.Upload.js')}" type="text/javascript"></script>
% else:
    % if request.registry.settings.get('allow_cdn'):
    <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
    <script src="http://ajax.aspnetcdn.com/ajax/jquery.templates/beta1/jquery.tmpl.min.js"></script>
    % else:
    <script src="${request.static_path('pygall:static/lib/jquery-ui/jquery-ui-1.8.16.min.js')}"></script>
    <script src="${request.static_path('pygall:static/lib/jquery-tmpl/jquery-tmpl-beta1.min.js')}"></script>
    % endif
    <script src="${request.static_path('pygall:static/build/upload.min.js')}"></script>
% endif

    <script type="text/javascript">
        $(document).ready($.proxy(App.Upload.init, undefined, ${maxfilesize}, ${minfilesize}));
    </script>
</%def>\
\


