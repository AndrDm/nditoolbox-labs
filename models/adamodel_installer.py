"""adamodel_installer.py - fetches and installs ADA Models

Chris R. Coughlin (TRI/Austin, Inc.) and John C. Aldrin (Computational Tools)
"""

from controllers import pathfinder
from models import podmodel_installer
from models.fetcher import Fetcher
from models.zipper import UnZipper
from models.mainmodel import get_logger
import os.path

module_logger = get_logger(__name__)

class ADAModelInstaller(podmodel_installer.PODModelInstaller):
    """Subclass of PluginInstaller:  installs local ADA Model archives, supports global
    passwords on ZIPs."""

    def __init__(self, plugin_url, zip_password=None):
        super(ADAModelInstaller, self).__init__(plugin_url, zip_password)

    def install_plugin(self):
        """Installs the ADA model in the default ADA models path.  Returns True if installation succeeded."""
        plugin_path = pathfinder.adamodels_path()
        if self.plugin is not None:
            plugin_zip = UnZipper(self.plugin_contents, self.zip_password)
            if self.verify_plugin():
                plugin_files = [each_file for each_file in plugin_zip.list_contents() if
                                each_file not in self.readme_files]
                for each_file in plugin_files:
                    plugin_zip.extract(each_file, plugin_path)
                    if not os.path.exists(os.path.join(plugin_path, each_file)):
                        module_logger.warning("Plugin installation failed.")
                        return False
            else:
                module_logger.warning("Plugin installation failed - plugin does not conform to spec.")
                return False
        else:
            module_logger.warning("Plugin installation failed - plugin is not set.")
            return False
        return True

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