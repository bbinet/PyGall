from ConfigParser import ConfigParser, NoOptionError
from pyramid.threadlocal import get_current_registry


def groupfinder(userid, request):
    groups = []
    cfg = ConfigParser()
    #TODO: get rid of this threadlocal call
    with open(get_current_registry().settings['groups_cfg']) as f:
        cfg.readfp(f)
        try:
            groups = cfg.get("user:groups", userid).split()
        except NoOptionError:
            pass
    return groups

def authenticate(login, password):
    #TODO: get rid of this threadlocal call
    with open(get_current_registry().settings['users_htpasswd'], 'r') as f:
        for line in f:
            try:
                username, hashed = line.rstrip().split(':', 1)
            except ValueError:
                continue
            if username == login and crypt_check(password, hashed):
                return username
    return None

def crypt_check(password, hashed):
    from crypt import crypt
    salt = hashed[:2]
    return hashed == crypt(password, salt)
