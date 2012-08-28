"""adamodel_installer.py - fetches and installs ADA Models

Chris R. Coughlin (TRI/Austin, Inc.) and John C. Aldrin (Computational Tools)
"""

from models import podmodel_installer
from models.fetcher import Fetcher

class ADAModelInstaller(podmodel_installer.PODModelInstaller):
    """Subclass of PluginInstaller:  installs local ADA Model archives, supports global
    passwords on ZIPs."""

    def __init__(self, plugin_url, zip_password=None):
        super(ADAModelInstaller, self).__init__(plugin_url, zip_password)


class RemoteADAModelInstaller(ADAModelInstaller):
    """Fetches and installs remote ADA models.  Supports
    HTTP Basic Auth and global passwords on ZIP archives."""

    def __init__(self, plugin_url, username=None, password=None, zip_password=None):
        self.plugin_url = plugin_url
        self.plugin_url_username = username
        self.plugin_url_password = password
        self.zip_password = zip_password
        self.plugin = None

    def fetch(self):
        """Retrieves the remote plugin, raising IOError if
        file not found / server unavailable."""
        plugin_fetcher = Fetcher(self.plugin_url, self.plugin_url_username,
                                 self.plugin_url_password)
        self.plugin = plugin_fetcher.fetch()