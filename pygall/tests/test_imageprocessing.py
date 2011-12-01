from unittest import TestCase


class ImageProcessingTests(TestCase):

    def test_constructor(self):
        from pygall.lib.imageprocessing import ImageProcessing
        from mock import patch
        with patch.object(ImageProcessing, 'set_dest_dir') as mock_set_dest_dir:
            ip = ImageProcessing()
            # check default values
            self.assertEqual(ip.dimension, 700)
            self.assertEqual(ip.quality, 80)
            # assert set_dest_dir has been called
            mock_set_dest_dir.assert_called_once_with(None)

