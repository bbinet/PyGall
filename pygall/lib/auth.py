from repoze.what.plugins.quickstart import setup_sql_auth

from pygall.model.meta import Session
from pygall.model.auth import User, Group, Permission


def AuthMiddleware(app, config):
    """
    Add authentication and authorization middleware to the ``app``.

    """

    # we need to provide repoze.what with translations as described here:
    # http://what.repoze.org/docs/plugins/quickstart/
    return setup_sql_auth(
            app,
            User,
            Group,
            Permission,
            Session,
            login_url='/account/login',
            post_login_url='/account/login',
            post_logout_url='/',
            login_handler='/account/login_handler',
            logout_handler='/account/logout',
            cookie_secret=config.get('sa_auth.cookie_secret'),
            translations={
                'user_name': 'name',
                'group_name': 'name',
                'permission_name': 'name',
                })
