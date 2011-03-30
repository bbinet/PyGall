"""Setup the PyGall application"""
import logging

import pylons.test

from pygall.config.environment import load_environment
from pygall.model.meta import Session, Base
from pygall.model.auth import User, Group, Permission

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup pygall here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=Session.bind)

    log.info("Adding initial users, groups and permissions...")
    g = Group()
    g.name = u'admin'
    g.description = u'Group of administrators'
    Session.add(g)

    p = Permission()
    p.name = u'admin'
    p.description = u'Admin permission'
    p.groups.append(g)
    Session.add(p)

    u = User()
    u.name = u'admin'
    passwd = raw_input("Enter password for user 'admin' [admin]: ") or "admin"
    u.password = passwd
    u.email_adress = u'admin@example.com'
    u.description = u'Admin user'
    u.groups.append(g)
    Session.add(u)
    log.info("User 'admin' with password '%s' has been added" % passwd)

    Session.commit()
