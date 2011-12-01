from unittest import TestCase


class ImageProcessingTests(TestCase):

    def test_constructor_no_arg(self):
        from pygall.lib.imageprocessing import ImageProcessing
        from mock import patch
        with patch.object(ImageProcessing, 'set_dest_dir') as mock_set_dest_dir:
            ip = ImageProcessing()
            # check default values
            self.assertEqual(ip.dimension, 700)
            self.assertEqual(ip.quality, 80)
            # assert set_dest_dir has been called
            mock_set_dest_dir.assert_called_once_with(None)

    def test_constructor_with_args(self):
        from pygall.lib.imageprocessing import ImageProcessing
        from mock import patch
        with patch.object(ImageProcessing, 'set_dest_dir') as mock_set_dest_dir:
            ip = ImageProcessing(
                    dest_dir='/foo/bar',
                    crop_dimension=100,
                    crop_quality=50)
            # check default values
            self.assertEqual(ip.dimension, 100)
            self.assertEqual(ip.quality, 50)
            # assert set_dest_dir has been called
            mock_set_dest_dir.assert_called_once_with('/foo/bar')

    def test_set_dest_dir(self):
        from pygall.lib.imageprocessing import ImageProcessing
        ip = ImageProcessing()
        ip.set_dest_dir('/foo/bar')
        self.assertEqual(ip.dest_dir, '/foo/bar')
        self.assertEqual(ip.abs_orig_dest_dir,  '/foo/bar/orig')
        self.assertEqual(ip.abs_scaled_dest_dir, '/foo/bar/scaled')

    def test_set_dest_dir_None(self):
        from pygall.lib.imageprocessing import ImageProcessing
        ip = ImageProcessing()
        ip.set_dest_dir(None)
        self.assertTrue(ip.dest_dir is None)
        self.assertTrue(ip.abs_orig_dest_dir is None)
        self.assertTrue(ip.abs_scaled_dest_dir is None)
