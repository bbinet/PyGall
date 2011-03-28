App = window.App || {};

App.urls = {
    photos_editcomment: "${url(controller='photos', action='editcomment')}",
    photos: "${url('photos')}"
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
