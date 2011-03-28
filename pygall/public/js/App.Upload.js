App = window.App || {};

App.Upload = (function() {
    var setupForm = function() {
        $("#upload").html("");
        $("#upload").fileUpload({
            action: App.urls.photos,
            submit_label: App._["Send file"],
            max_size_error_label: App._["File is too big"],
            success: function() {
                $('#flash').text(App._["Upload was successful"]);
                setupForm();
            },
            error: function() {
                $('#flash').text(App._["Upload has failed"]);
                setupForm();
            },
            submit_empty_forms: false
        });
    };

    return {
        init: function() {
            setupForm();
        }
    };
})();
