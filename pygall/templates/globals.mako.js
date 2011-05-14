if(!window.App) App = {};

App.urls = {
    home: "${request.route_url('home')}",
    root: "${request.static_url('pygall:static/')}"
};
