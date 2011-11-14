from unittest import TestCase

from pyramid import testing


class EntryTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_login(self):
        from pygall.views.entry import login
        request = testing.DummyRequest()
        r = login(request)

    def test_logout(self):
        from pygall.views.entry import logout
        headers = self.config.testing_securitypolicy(userid='admin')
        request = testing.DummyRequest()
        r = logout(request)
        #self.assertEqual(...)

