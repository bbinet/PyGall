from unittest import TestCase

from pyramid import testing


class PhotosTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

