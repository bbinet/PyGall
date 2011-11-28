import os
from unittest import TestCase

class BaseTestCase(TestCase):

    def setUp(self):
        from tempfile import mkstemp
        from pygall import main
        _, fn = mkstemp(suffix='.cfg', prefix='auth_')
        f = open(fn, 'wb')
        # setup 2 accounts: admin/admin - guest/guest
        f.write("admin:N5rIuAWOHGycs:admin\n" \
                "guest:Z7TjkT9L.lUAM\n")
        f.close()
        self.settings = {
            'sqlalchemy.url': 'sqlite:///:memory:',
            'auth_cfg': fn,
            'authtkt_secret': 'secret',
        }
        from webtest import TestApp
        self.testapp = TestApp(main({}, **self.settings))

    def tearDown(self):
        os.remove(self.settings['auth_cfg'])

    def _login(self, login):
        r = self.testapp.post('/login', params={
            'login': login,
            'password': login,
            'form.submitted': True,
            'came_from': '/login',
            })
        self.assertEqual(r.status_int, 302)
        return r

    def _logout(self):
        r = self.testapp.get('/logout')
        self.assertEqual(r.status_int, 302)
        return r


