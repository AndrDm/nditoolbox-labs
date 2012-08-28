"""test_adamodel_installer.py - tests the adamodel_installer module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import adamodel_installer as adamodel_installer
from models.tests import test_podmodel_installer
import models.zipper as zipper
import random
import SimpleHTTPServer
import SocketServer
import threading

class TestADAModelInstaller(test_podmodel_installer.TestPODModelInstaller):
    """Tests the ADAModelInstaller class"""

    def setUp(self):
        self.good_plugin_installer = adamodel_installer.ADAModelInstaller(self.good_plugin_loc)
        self.plugin_reader = zipper.UnZipper(self.good_plugin_loc)

    @property
    def good_plugin_loc(self):
        """Returns the full path to the known good ADA model archive."""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('good_adamodel.zip')

    @property
    def badfolders_plugin_loc(self):
        """Returns the full path to a known bad ADA model (support folders must share the name
        of the ADA model archive)"""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('badfolders_adamodel.zip')

    @property
    def badname_plugin_loc(self):
        """Returns the full path to a known bad ADA model (root plugin module must share the name of the
         plugin archive)"""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('badname_adamodel.zip')

    @property
    def badnomodule_plugin_loc(self):
        """Returns the full path to a known bad ADA model (root plugin module must exist)"""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('badnomodule_adamodel.zip')

    @property
    def badreadme_plugin_loc(self):
        """Returns the full path to a known bad ADA model (plugin archive must have a properly-named
        README file)"""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('badreadme_adamodel.zip')

    @property
    def badnoreadme_plugin_loc(self):
        """Returns the full path to a known bad ADA model (plugin archive must have a README file)"""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('badnoreadme_adamodel.zip')

    @property
    def badstructure_plugin_loc(self):
        """Returns the full path to a known bad ADA model (plugin may only have a .py module, .cfg config file,
        and a README file in the root)"""
        return test_podmodel_installer.TestPODModelInstaller.local_plugin('badstructure_adamodel.zip')

class TestRemoteADAModelInstaller(test_podmodel_installer.TestRemotePODModelInstaller):
    """Tests the RemoteADAModelInstaller class"""

    @classmethod
    def setUpClass(cls):
        """Create a SimpleHTTPServer instance to serve test files from the support_files folder"""
        cls.PORT = 8000 + random.randint(1, 1000)
        req_handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        cls.httpd = SocketServer.TCPServer(("localhost", cls.PORT), req_handler)
        cls.httpd.timeout = 5

    @property
    def good_plugin(self):
        """Returns the path and filename to the known good ADA model"""
        return TestRemoteADAModelInstaller.local_plugin('good_adamodel.zip')

    @property
    def good_plugin_url(self):
        """Returns the URL to the known good ADA model"""
        return TestRemoteADAModelInstaller.plugin_url('good_adamodel.zip')

    @property
    def badfolders_plugin_url(self):
        """Returns the URL to a known bad ADA model (support folders must share name of the plugin archive)"""
        return TestRemoteADAModelInstaller.plugin_url('badfolders_adamodel.zip')

    @property
    def badname_plugin_url(self):
        """Returns the URL to a known bad ADA model (root plugin module must share the name of the plugin
        archive)"""
        return TestRemoteADAModelInstaller.plugin_url('badname_adamodel.zip')

    @property
    def badnomodule_plugin_url(self):
        """Returns the URL to a known bad ADA model (root plugin module must exist)"""
        return TestRemoteADAModelInstaller.plugin_url('badnomodule_adamodel.zip')

    @property
    def badreadme_plugin_url(self):
        """Returns the URL to a known bad ADA model (plugin archive must have a properly-named README)"""
        return TestRemoteADAModelInstaller.plugin_url('badreadme_adamodel.zip')

    @property
    def badnoreadme_plugin_url(self):
        """Returns the URL to a known bad ADA model (plugin archive must have a README file)"""
        return TestRemoteADAModelInstaller.plugin_url('badnoreadme_adamodel.zip')

    @property
    def badstructure_plugin_url(self):
        """Returns the URL to a known bad ADA model (plugin may only have a .py module, .cfg config file,
        and a README file in the root)"""
        return TestRemoteADAModelInstaller.plugin_url('badstructure_podmodel.zip')

    def setUp(self):
        """Creates a SimpleHTTPServer instance to handle a single
        request.  Use self.server_thd.start() to initiate."""
        self.server_thd = threading.Thread(target=TestRemoteADAModelInstaller.httpd.handle_request)
        self.good_plugin_installer = adamodel_installer.RemoteADAModelInstaller(self.good_plugin_url)
        self.plugin_reader = zipper.UnZipper(self.good_plugin)

if __name__ == "__main__":
    random.seed()
    unittest.main()