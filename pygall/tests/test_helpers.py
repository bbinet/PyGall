from unittest import TestCase


class HelpersTests(TestCase):

    def test_mkdir_p(self):
        import os
        import shutil
        from tempfile import mkdtemp
        from pygall.lib.helpers import mkdir_p
        tmpdir = mkdtemp(prefix='test_mkdir_p-')
        testpath = os.path.join(tmpdir, 'dummy', 'directory')
        mkdir_p(testpath)
        self.assertTrue(os.path.isdir(testpath))
        # test that no exception is raised if testpath already exists
        mkdir_p(testpath)
        self.assertTrue(os.path.isdir(testpath))
        shutil.rmtree(tmpdir)
        from mock import patch
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = OSError
            self.assertRaises(OSError, mkdir_p, testpath)

    def test_get_size(self):
        from pygall.lib.helpers import get_size
        src = 'python.jpg'
        size = get_size(src)
        self.assertEqual(size, 63205)
        # test get_size of a file object
        with open(src, 'rb') as f:
            size = get_size(f)
            self.assertEqual(size, 63205)

    def test_img_md5(self):
        from pygall.lib.helpers import img_md5
        src = 'python.jpg'
        md5 = img_md5(src)
        self.assertEqual(md5, '065c540533e7621f6fc37fb9ab297b3f')
        # test img_md5 of a file object
        with open(src, 'rb') as f:
            md5 = img_md5(f)
            self.assertEqual(md5, '065c540533e7621f6fc37fb9ab297b3f')

    def test_unchroot_path(self):
        import os
        import shutil
        from tempfile import mkdtemp
        from pygall.lib.helpers import unchroot_path
        self.assertRaises(Exception, unchroot_path, None, None)
        self.assertRaises(
                Exception, unchroot_path, '/path/to/file', '/bad/chroot')
        self.assertRaises(
                Exception, unchroot_path, '/path/to/file', '/chroot/path')
        self.assertRaises(
                Exception, unchroot_path, '/path..//etc/passwd', '/chroot/path')
        # test a working unchroot_path
        tmpdir = mkdtemp(prefix='test_unchroot_path-')
        testpath = os.path.join(tmpdir, 'dummy', 'file')
        os.makedirs(os.path.dirname(testpath), 0755)
        open(testpath, 'w').close() # create a dest file
        pth = unchroot_path('/dummy/file', os.path.join(tmpdir, 'dummy'))
        self.assertEqual(pth, (testpath, 'file'))
        shutil.rmtree(tmpdir)
