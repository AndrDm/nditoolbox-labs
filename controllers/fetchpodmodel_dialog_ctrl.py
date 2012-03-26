"""fetchpodmodel_dialog_ctrl.py - controllers for the fetchpodmodel_dialogs

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import fetchplugin_dialog_ctrl as fetchplugin
from models import fetchpodmodel_dialog_model
import wx

class FetchPODModelDialogController(fetchplugin.FetchPluginDialogController):
    """Controller for the FetchPODModelDialog"""

    def __init__(self, view):
        self.view = view
        self.model = fetchpodmodel_dialog_model.FetchPODModelDialogModel(self)
        self.init_url()

    def install_plugin(self):
        """Downloads, verifies, and installs the plugin"""
        try:
            self.fetch_plugin()
            if not self.model.install_plugin():
                err_dlg = wx.MessageDialog(self.view, message="POD Model installation failed.",
                                           caption="Unable To Install POD Model",
                                           style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            else:
                success_dlg = wx.MessageDialog(self.view,
                                               message="POD Model installation successful.",
                                               caption="Installation Complete",
                                               style=wx.ICON_INFORMATION)
                success_dlg.ShowModal()
                success_dlg.Destroy()
        except Exception as err:
            err_msg = "{0}".format(err)
            if err_msg == "":
                err_msg = "An error occurred during the installation process."
            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                       caption="Unable To Install POD Model", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()


class FetchRemotePODModelDialogController(fetchplugin.FetchRemotePluginDialogController):
    """Controller for the FetchRemotePODModelDialog"""

    def __init__(self, view):
        self.view = view
        self.model = fetchpodmodel_dialog_model.FetchRemotePODModelDialogModel(self)
        self.init_url()

    def init_controller(self):
        """Creates the view's controller"""
        self.controller = fetchplugin.FetchRemotePluginDialogController(self)