from pygall.tests import *

class TestDatesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='dates', action='index'))
        # Test response...
