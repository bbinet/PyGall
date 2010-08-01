from pygall.tests import *

class TestImportController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='import', action='index'))
        # Test response...
