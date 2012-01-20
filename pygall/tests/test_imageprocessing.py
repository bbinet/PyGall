from unittest import TestCase


class UtilitiesTests(TestCase):

    def test_get_exif(self):
        import Image
        from pygall.lib.imageprocessing import get_exif
        self.assertRaises(Exception, get_exif, None)
        im = Image.open('python.jpg')
        exif = get_exif(im._getexif())
        self.assertEqual(exif['DateTimeOriginal'], '2011:11:27 15:08:47')
        self.assertEqual(exif['Orientation'], 1)

    def test_get_info(self):
        from pygall.lib.imageprocessing import get_info
        from datetime import datetime
        from contextlib import nested
        from mock import patch
        with nested(
                patch('pygall.lib.imageprocessing.get_exif'),
                patch('pygall.lib.imageprocessing.img_md5'),
                patch('pygall.lib.imageprocessing.get_size'),
                ) as (mock_get_exif, mock_img_md5, mock_get_size):
            mock_get_exif.return_value = {
                    'DateTimeOriginal': '2000:12:31 23:00:00'
                    }
            mock_img_md5.return_value = 'dummy_md5sum'
            mock_get_size.return_value = 'dummy_size'
            info = get_info('python.jpg')
            self.assertEqual(info, {
                'date': datetime(2000, 12, 31, 23, 0, 0),
                'ext': 'jpeg',
                'md5sum': 'dummy_md5sum',
                'size': 'dummy_size',
                })

            # test date:None if invalid date
            mock_get_exif.return_value = {
                    'DateTimeOriginal': 'ERROR'
                    }
            info = get_info('python.jpg')
            self.assertEqual(info['date'], None)

            # test that existing info param is given priority over calculation
            info = get_info('python.jpg', {
                'date': 'fake_date',
                'ext': 'fake_ext',
                'md5sum': 'fake_md5sum',
                'size': 'fake_size',
                })
            self.assertEqual(info, {
                'date': 'fake_date',
                'ext': 'fake_ext',
                'md5sum': 'fake_md5sum',
                'size': 'fake_size',
                })

    def test_get_info_fileobj(self):
        from pygall.lib.imageprocessing import get_info
        from datetime import datetime
        with open('python.jpg', 'rb') as src:
            loc = src.tell()
            info = get_info(src)
            self.assertEqual(info, {
                'date': datetime(2011, 11, 27, 15, 8, 47),
                'ext': 'jpeg',
                'md5sum': u'065c540533e7621f6fc37fb9ab297b3f',
                'size': 63205
                })
            self.assertEqual(src.tell(), loc)


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

    def test_copy_scaled_already_exists(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'scaled', uri)
        os.makedirs(os.path.dirname(dest), 0755)
        open(dest, 'w').close() # create a dest file
        self.assertFalse(self.ip.copy_scaled('python.jpg', uri))

    def test_copy_scaled(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'scaled', uri)
        self.ip.copy_scaled('python.jpg', uri)
        self.assertTrue(os.path.exists(dest))
        with open(dest, 'rb') as f:
            self.assertEqual(
                    hashlib.md5(f.read()).hexdigest(),
                    'af18318b71016ea25e2c79c63810482a')

    def test_copy_scaled_with_rotation(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'scaled', uri)
        from mock import patch
        with patch('pygall.lib.imageprocessing.get_exif') as mock_get_exif:
            mock_get_exif.return_value = {'Orientation': 6}
            self.ip.copy_scaled('python.jpg', uri)
            self.assertTrue(os.path.exists(dest))
            with open(dest, 'rb') as f:
                self.assertEqual(
                        hashlib.md5(f.read()).hexdigest(),
                        'aa72c5f0442e45f413102b5dc022141b')
            self.assertEqual(mock_get_exif.called, 1)
            os.unlink(dest)

            # test that if an exception occurs, there is no rotation
            mock_get_exif.side_effect = Exception()
            self.ip.copy_scaled('python.jpg', uri)
            with open(dest, 'rb') as f:
                self.assertEqual(
                        hashlib.md5(f.read()).hexdigest(),
                        'af18318b71016ea25e2c79c63810482a')

    def test_copy_scaled_fileobj(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest = os.path.join(self.destdir, 'scaled', uri)
        with open('python.jpg', 'rb') as src:
            loc = src.tell()
            self.ip.copy_scaled(src, uri)
            self.assertTrue(os.path.exists(dest))
            with open(dest, 'rb') as f:
                self.assertEqual(
                        hashlib.md5(f.read()).hexdigest(),
                        'af18318b71016ea25e2c79c63810482a')
            self.assertEqual(src.tell(), loc)

    def test_remove_image(self):
        import os
        import hashlib
        uri = 'test/python.jpg'
        dest_orig = os.path.join(self.destdir, 'orig', uri)
        dest_scaled = os.path.join(self.destdir, 'scaled', uri)
        os.makedirs(os.path.dirname(dest_orig), 0755)
        os.makedirs(os.path.dirname(dest_scaled), 0755)
        open(dest_orig, 'w').close() # create a dest_orig file
        open(dest_scaled, 'w').close() # create a dest_scaled file
        self.assertTrue(os.path.exists(dest_orig))
        self.assertTrue(os.path.exists(dest_scaled))
        self.ip.remove_image(uri)
        self.assertFalse(os.path.exists(dest_orig))
        self.assertFalse(os.path.exists(dest_scaled))
        # test removal does not crash if dest images don't exist
        self.ip.remove_image(uri)
        self.assertFalse(os.path.exists(dest_orig))
        self.assertFalse(os.path.exists(dest_scaled))

    def test_process_image(self):
        from contextlib import nested
        from datetime import datetime
        from pygall.lib.imageprocessing import ImageProcessing
        from mock import patch
        src = 'python.jpg'
        with nested(
                patch('pygall.lib.imageprocessing.get_info'),
                patch.object(ImageProcessing, 'copy_orig'),
                patch.object(ImageProcessing, 'copy_scaled'),
                patch.object(ImageProcessing, 'remove_image'),
                ) as (mock_get_info, mock_copy_orig, mock_copy_scaled,
                        mock_remove_image):
            mock_get_info.return_value = {
                    'md5sum': 'the_md5',
                    'date': datetime(2002, 02, 22),
                    'ext': 'jpeg',
                    }
            info = self.ip.process_image(src, md5sum='dummy_md5sum')
            uri = info['uri']
            self.assertEqual(uri, '2002/02/22/the_md5.jpeg')
            mock_copy_orig.assert_called_once_with(src, uri)
            mock_copy_scaled.assert_called_once_with(src, uri)
            # test if an exception is thrown
            mock_copy_scaled.side_effect = Exception()
            self.assertRaises(Exception, self.ip.process_image, src)
            mock_remove_image.assert_called_once_with(uri)
