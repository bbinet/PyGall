from ConfigParser import ConfigParser, NoOptionError
from pyramid.threadlocal import get_current_registry


def _get_auth(userid):
    #TODO: get rid of this threadlocal call
    with open(get_current_registry().settings['auth_cfg'], 'r') as f:
        for l in f:
            line = l.strip()
            if line.startswith('#'):
                continue
            tokens = line.rstrip().split(':')
            if tokens[0] == userid:
                return tokens
    return None

def groupfinder(userid, request):
    tokens = _get_auth(userid)
    if tokens and len(tokens) == 3:
        return [tokens[2]]
    else:
        return []

def authenticate(login, password):
    tokens = _get_auth(login)
    if tokens and len(tokens) > 1 and _crypt_check(password, tokens[1]):
        return login
    return None

def _crypt_check(password, hashed):
    from crypt import crypt
    salt = hashed[:2]
    return hashed == crypt(password, salt)
