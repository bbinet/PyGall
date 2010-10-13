# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

"""
import os
from datetime import datetime
import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, synonym

from pygall.model.meta import Base, Session

__all__ = ['User', 'Group', 'Permission']


# Association tables


# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table('group_permission', Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permission.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table('user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('group.id',
        onupdate="CASCADE", ondelete="CASCADE"))
)


# The auth* model itself


class Group(Base):
    """
    Group definition for :mod:`repoze.what`.

    Only the ``name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'group'

    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(24), unique=True, nullable=False)
    description = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

    # Relations
    users = relation('User', secondary=user_group_table, backref='groups')

    # Special methods

    def __repr__(self):
        return '<Group: name=%s>' % self.name

    def __unicode__(self):
        return self.name



class User(Base):
    """
    User definition.

    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``name`` column.

    """
    __tablename__ = 'user'

    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(24), unique=True, nullable=False)
    email_address = Column(Unicode(255), unique=True)
    description = Column(Unicode(255))
    _password = Column('password', Unicode(80))
    created = Column(DateTime, default=datetime.now)

    # Special methods

    def __repr__(self):
        return '<User: email="%s", display name="%s">' % (
                self.email_address, self.description)

    def __unicode__(self):
        return self.description or self.name

    # Getters and setters

    @property
    def permissions(self):
        """Return a set of strings for the permissions granted."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return Session.query(cls).filter(cls.email_address==email).first()

    @classmethod
    def by_user_name(cls, username):
        """Return the user object whose user name is ``username``."""
        return Session.query(cls).filter(cls.name==username).first()

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        # Make sure the hashed password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # columns
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))

    #

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()


class Permission(Base):
    """
    Permission definition for :mod:`repoze.what`.

    Only the ``name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'permission'

    # Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(24), unique=True, nullable=False)
    description = Column(Unicode(255))

    # Relations
    groups = relation(Group, secondary=group_permission_table,
                      backref='permissions')

    # Special methods

    def __repr__(self):
        return '<Permission: name=%s>' % self.name

    def __unicode__(self):
        return self.name

