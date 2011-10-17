import logging
import os


log = logging.getLogger(__name__)
auth_cfg = {}

def init_security(settings):
    if not os.path.exists(settings['auth_cfg']):
        log.warn('can\'t read auth configuration from file "%s": ' \
                'No such file' % settings['auth_cfg'])
        return None
    with open(settings['auth_cfg'], 'r') as f:
        for l in f:
            line = l.strip()
            if line.startswith('#'):
                continue
            tokens = line.rstrip().split(':')
            if len(tokens) > 1:
                auth_cfg[tokens[0]] = \
                    (tokens[1], (tokens[2],) if len(tokens)==3 else ())

def groupfinder(userid, request):
    return auth_cfg[userid][1]

def authenticate(login, password):
    if login in auth_cfg and _crypt_check(password, auth_cfg[login][0]):
        return login

def _crypt_check(password, hashed):
    from crypt import crypt
    salt = hashed[:2]
    return hashed == crypt(password, salt)
