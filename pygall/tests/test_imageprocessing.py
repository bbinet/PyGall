from unittest import TestCase


class IPMockTests(TestCase):

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


class IPTests(TestCase):

    def setUp(self):
        from tempfile import mkdtemp
        from pygall.lib.imageprocessing import ImageProcessing
        self.destdir = mkdtemp(prefix='test_ip_')
        self.ip = ImageProcessing(
                dest_dir=self.destdir,
                crop_dimension=700,
                crop_quality=80)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.destdir)

    def test_copy_orig_already_exists(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'orig', uri)
        os.makedirs(os.path.dirname(dest), 0755)
        open(dest, 'w').close() # create a dest file
        self.assertFalse(self.ip.copy_orig('python.jpg', uri))

    def test_copy_orig(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'orig', uri)
        self.ip.copy_orig('python.jpg', uri)
        self.assertTrue(os.path.exists(dest))
        with open(dest, 'rb') as f:
            self.assertEqual(
                    hashlib.md5(f.read()).hexdigest(),
                    '4c6f6da9406bce4ae220d265aa70f9d9')

    def test_copy_orig_fileobj(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'orig', uri)
        with open('python.jpg', 'rb') as src:
            loc = src.tell()
            self.ip.copy_orig(src, uri)
            self.assertTrue(os.path.exists(dest))
            with open(dest, 'rb') as f:
                self.assertEqual(
                        hashlib.md5(f.read()).hexdigest(),
                        '4c6f6da9406bce4ae220d265aa70f9d9')
            self.assertEqual(src.tell(), loc)
