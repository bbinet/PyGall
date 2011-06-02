from pyramid.threadlocal import get_current_registry


USERS = {
    'admin': ['group:admin'],
    'user': []
}

def groupfinder(userid, request):
    if userid in USERS:
        return USERS[userid]

def authenticate(login, password):
    #TODO: get rid of this threadlocal call
    settings = get_current_registry().settings
    f = open(settings['users_htpasswd'], 'r')
    for line in f:
        try:
            username, hashed = line.rstrip().split(':', 1)
        except ValueError:
            continue
        if username == login:
            if crypt_check(password, hashed):
                return username
    return None

def crypt_check(password, hashed):
    from crypt import crypt
    salt = hashed[:2]
    return hashed == crypt(password, salt)
