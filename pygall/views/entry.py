from pyramid.view import view_config
from pyramid.security import remember, forget, authenticated_userid
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPFound

from pygall.security import authenticate


@view_config(context=Forbidden)
def forbidden_view(request):
    if not authenticated_userid(request):
        return HTTPFound(location = request.route_path('login'))
    return Forbidden()

@view_config(route_name='login', renderer='login.html.mako')
def login(request):
    referrer = request.referrer or request.url
    if referrer == request.route_url('login'):
        # never use the login form itself as came_from
        referrer = request.route_path('photos_index', page='')
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login'].strip()
        password = request.params['password']
        if authenticate(login, password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        came_from = came_from,
        login = login,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_path('login'),
                     headers = headers)

