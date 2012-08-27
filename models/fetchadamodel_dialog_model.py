"""fetchadamodel_dialog_model.py - models for the FetchADAModelDialogs

Chris R. Coughlin (TRI/Austin, Inc.) and John C. Aldrin
"""

__author__ = 'Chris R. Coughlin and John C. Aldrin'

from models import fetchplugin_dialog_model as fetchplugin_model
from models import adamodel_installer

class FetchADAModelDialogModel(fetchplugin_model.FetchPluginDialogModel):
    """Model for the FetchADAModelDialog"""

    def __init__(self, controller):
        super(FetchADAModelDialogModel, self).__init__(controller)

    def get_plugin(self, url_dict):
        """Fetches the plugin"""
        plugin_url = url_dict.get('url')
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
        else:
            zip_password = None
        self.plugin_fetcher = adamodel_installer.ADAModelInstaller(plugin_url, zip_password)
        self.plugin_fetcher.fetch()


class FetchRemoteADAModelDialogModel(fetchplugin_model.FetchRemotePluginDialogModel):
    """Model for the FetchRemoteADAModelDialog"""

    def __init__(self, controller):
        super(FetchRemoteADAModelDialogModel, self).__init__(controller)

    def get_plugin(self, url_dict):
        """Downloads the plugin"""
        plugin_url = url_dict.get('url')
        if url_dict.get('login', False):
            username = url_dict.get('username')
            password = url_dict.get('password')
        else:
            username = None
            password = None
        if url_dict.get('zip_encrypted', False):
            zip_password = url_dict.get('zip_password')
        else:
            zip_password = None
        self.plugin_fetcher = adamodel_installer.RemoteADAModelInstaller(plugin_url, username,
                                                                         password, zip_password)
        self.plugin_fetcher.fetch()