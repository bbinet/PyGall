App = window.App || {};

App.Upload = (function() {
    var setupForm = function(maxfilesize, minfilesize) {
        'use strict';

        // Initialize the jQuery File Upload widget
        // For a complete option reference go to
        // https://github.com/blueimp/jQuery-File-Upload
        $('#fileupload').fileupload({
            // this formData is neccessary to pass the csrf and pass uid to django
            //formData: [
                //{ name: "uid", value: "{{ uid }}"},
                //{ name: "csrfmiddlewaretoken", value: "{{ csrf_token }}"}
            //],
            maxFileSize: maxfilesize,
            minFileSize: minfilesize,
            sequentialUploads: false
        });

        // Load existing files
        $.getJSON($('#fileupload form').prop('action'), function (files) {
            var fu = $('#fileupload').data('fileupload');
            fu._adjustMaxNumberOfFiles(-files.length);
            fu._renderDownload(files)
                    .appendTo($('#fileupload .files'))
                    .fadeIn(function () {
                        // Fix for IE7 and lower:
                        $(this).show();
                    });
        });

        // Open download dialogs via iframes,
        // to prevent aborting current uploads
        $('#fileupload .files a:not([target^=_blank])').live('click', function (e) {
            e.preventDefault();
            $('<iframe style="display:none;"></iframe>')
                    .prop('src', this.href)
                    .appendTo('body');
        });
    };

    return {
        init: function(maxfilesize, minfilesize) {
            setupForm(maxfilesize, minfilesize);
        }
    };
})();
