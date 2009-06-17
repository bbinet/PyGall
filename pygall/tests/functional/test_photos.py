from pygall.tests import *

class TestPhotosController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='photos', action='index'))
        # Test response...
