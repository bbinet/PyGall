from unittest import TestCase

from pyramid import testing


class EntryTests(TestCase):

    def setUp(self):
        from pygall import main
        settings = {
            'sqlalchemy.url': 'sqlite:///:memory:'
        }
        self.app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def test_login(self):
        r = self.testapp.get('/login', params={
            'login': 'foo',
            'password': 'bar'
            })
        #self.assertEqual(...)

    def test_logout(self):
        from pygall.views.entry import logout
        headers = self.config.testing_securitypolicy(userid='admin')
        request = testing.DummyRequest()
        r = logout(request)
        #self.assertEqual(...)

