App = window.App || {};

App.constants = {

    edit: false,

    urls: {

        photos_editcomment: "${url(controller='photos', action='editcomment')}",

        photos: "${url('photos')}",

        import_delete: "${url(controller='import', action='delete')}"
    }
};

