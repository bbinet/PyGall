from pygall.tests.functional import BaseTestCase


class EntryTests(BaseTestCase):

    def test_login_referer(self):
        r = self.testapp.get(
                '/login', extra_environ={'HTTP_REFERER': '/referer'})
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.forms[0].fields['came_from'][0].value, '/referer')

    def test_login_no_referer(self):
        r = self.testapp.get('/login')
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.forms[0].fields['came_from'][0].value, '/')

    def test_login_guest(self):
        r = self.testapp.post('/login', params={
            'login': 'guest',
            'password': 'guest',
            'form.submitted': True,
            'came_from': '/login',
            })
        self.assertEqual(r.status_int, 302)
        self.assertEqual(r.location, 'http://localhost/login')
        r = r.follow()
        self.assertEqual(r.status_int, 200)
        self.assertFalse(u'Failed login' in r.body)
        self.assertTrue('<a href="/"' in r.body)
        self.assertTrue('<a href="/logout"' in r.body)
        self.assertFalse('<a href="/photos/new"' in r.body)
        self.assertFalse('<a href="/admin/"' in r.body)

    def test_login_admin(self):
        r = self.testapp.post('/login', params={
            'login': 'admin',
            'password': 'admin',
            'form.submitted': True,
            'came_from': '/login',
            })
        self.assertEqual(r.status_int, 302)
        self.assertEqual(r.location, 'http://localhost/login')
        r = r.follow()
        self.assertEqual(r.status_int, 200)
        self.assertFalse(u'Failed login' in r.body)
        self.assertTrue('<a href="/"' in r.body)
        self.assertTrue('<a href="/logout"' in r.body)
        self.assertTrue('<a href="/photos/new"' in r.body)
        self.assertTrue('<a href="/admin/"' in r.body)

    def test_login_failed(self):
        r = self.testapp.post('/login', params={
            'login': 'foo',
            'password': 'bar',
            'form.submitted': True,
            })
        self.assertEqual(r.status_int, 200)
        self.assertTrue(u'Failed login' in r.body)
        self.assertFalse('<a href="/"' in r.body)
        self.assertFalse('<a href="/logout"' in r.body)
        self.assertFalse('<a href="/photos/new"' in r.body)
        self.assertFalse('<a href="/admin/"' in r.body)

    def test_logout(self):
        r = self._login('guest')
        r = r.follow()
        self.assertEqual(r.status_int, 200)
        self.assertTrue('<a href="/"' in r.body)
        self.assertTrue('<a href="/logout"' in r.body)

        r = self.testapp.get('/logout')
        self.assertFalse('<a href="/"' in r.body)
        self.assertFalse('<a href="/logout"' in r.body)
        self.assertFalse('<a href="/photos/new"' in r.body)
        self.assertFalse('<a href="/admin/"' in r.body)
        self.assertTrue('<a href="/login"' in r.body)

    def test_forbidden_redirected(self):
        r = self.testapp.get('/')
        self.assertEqual(r.status_int, 302)
        self.assertEqual(r.location, 'http://localhost/login')

    def test_forbidden(self):
        r = self._login('guest')
        r = self.testapp.get('/admin')
        self.assertEqual(r.status_int, 302)
        self.assertEqual(r.location, 'http://localhost/admin/')
        r = r.follow(expect_errors=True)
        self.assertEqual(r.status_int, 403)

