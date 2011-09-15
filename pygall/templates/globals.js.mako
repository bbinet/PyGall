App = window.App || {};

App.urls = {
    photos_index: "${request.route_path('photos_index', page='')}",
    photos_new: "${request.route_path('photos_new')}",
    photos_create: "${request.route_path('photos_create')}"
};

// i18n
App._ = {
    "Send file": "${_("Send file")}",
    "File is too big": "${_("File is too big")}",
    "Upload was successful": "${_("Upload was successful")}",
    "Upload has failed": "${_("Upload has failed")}",
    "Enter a comment": "${_("Enter a comment")}",
    "Edit": "${_("Edit")}"
};
