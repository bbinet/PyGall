import os
from unittest import TestCase

from pyramid import testing


class EntryTests(TestCase):

    def setUp(self):
        from tempfile import mkstemp
        from pygall import main
        _, fn = mkstemp(suffix='.cfg', prefix='auth_')
        f = open(fn, 'wb')
        f.write("admin:N5rIuAWOHGycs:admin\n" \
                "guest:Z7TjkT9L.lUAM\n")
        f.close()
        self.settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'auth_cfg': fn,
            'authtkt_secret': 'secret',
        }
        self.app = main({}, **self.settings)
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def tearDown(self):
        os.remove(self.settings['auth_cfg'])

    def test_login(self):
        r = self.testapp.get('/login', params={
            'login': 'foo',
            'password': 'bar'
            })
        #self.assertEqual(...)

    def test_logout(self):
        pass

