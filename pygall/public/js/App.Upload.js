App = window.App || {};

App.Upload = (function() {
    var setupForm = function() {
        $("#upload").html("");
        $("#upload").fileUpload({
            action: App.constants.urls.photos,
            submit_label: "Envoyer",
            max_size_error_label: "Le fichier est trop gros",
            success: function() {
                $('#flash').text("L'envoi a réussi");
                setupForm();
            },
            error: function() {
                $('#flash').text("L'envoi a échoué");
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
