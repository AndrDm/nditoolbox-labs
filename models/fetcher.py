"""fetcher.py - retrieves files via HTTP/HTTPS

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models.mainmodel import get_logger
import urllib2

module_logger = get_logger(__name__)

class Fetcher(object):
    """Retrieves remote files via HTTP/HTTPS"""

    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        module_logger.info("Successfully initiated Fetcher.")

    def fetch_handle(self):
        """Returns the file-like object handle to the remote
        file.  Raises IOError if unable to contact server or
        request couldn't be completed (e.g. file not found)."""
        if self.url is not None:
            try:
                if self.username is not None and self.password is not None:
                    auth_handler = urllib2.HTTPBasicAuthHandler()
                    auth_handler.add_password(realm=None, uri=self.url,
                                              user=self.username, passwd=self.password)
                    opener = urllib2.build_opener(auth_handler)
                    urllib2.install_opener(opener)
                return urllib2.urlopen(self.url)
            except urllib2.HTTPError as e:
                # Couldn't complete request
                module_logger.error("Server couldn't complete request: {0}".format(e))
                raise IOError("The server couldn't complete the request.")
            except urllib2.URLError as e:
                # Couldn't connect to server
                module_logger.error("Unable to contact server: {0}".format(e))
                raise IOError("Unable to contact server.")

    def fetch(self):
        """Returns the remote file if found.  Raises
        IOError if unable to contact server or request
        couldn't be completed (e.g. file not found)."""
        if self.url is not None:
            try:
                remote_file_handle = self.fetch_handle()
                return remote_file_handle.read()
            except urllib2.HTTPError as e:
                # Couldn't complete request
                module_logger.error("Server couldn't complete request: {0}".format(e))
                raise IOError("The server couldn't complete the request.")
            except urllib2.URLError as e:
                # Couldn't connect to server
                module_logger.error("Unable to contact server: {0}".format(e))
                raise IOError("Unable to contact server.")