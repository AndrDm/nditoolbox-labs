"""fetchadamodel_dialog_ctrl.py - controllers for the fetchadamodel_dialogs

Chris R. Coughlin (TRI/Austin, Inc.) and John C. Aldrin
"""

__author__ = 'Chris R. Coughlin and John C. Aldrin'

from controllers import fetchplugin_dialog_ctrl as fetchplugin
from models import fetchadamodel_dialog_model
import wx

class FetchADAModelDialogController(fetchplugin.FetchPluginDialogController):
    """Controller for the FetchADAModelDialog"""

    def __init__(self, view):
        self.view = view
        self.model = fetchadamodel_dialog_model.FetchADAModelDialogModel(self)
        self.init_url()

    def install_plugin(self):
        """Downloads, verifies, and installs the plugin"""
        try:
            self.fetch_plugin()
            if not self.model.install_plugin():
                err_dlg = wx.MessageDialog(self.view, message="ADA Model installation failed.",
                                           caption="Unable To Install ADA Model",
                                           style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
            else:
                success_dlg = wx.MessageDialog(self.view,
                                               message="ADA Model installation successful.",
                                               caption="Installation Complete",
                                               style=wx.ICON_INFORMATION)
                success_dlg.ShowModal()
                success_dlg.Destroy()
        except Exception as err:
            err_msg = "{0}".format(err)
            if err_msg == "":
                err_msg = "An error occurred during the installation process."
            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                       caption="Unable To Install ADA Model", style=wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()


class FetchRemoteADAModelDialogController(fetchplugin.FetchRemotePluginDialogController):
    """Controller for the FetchRemoteADAModelDialog"""

    def __init__(self, view):
        self.view = view
        self.model = fetchadamodel_dialog_model.FetchRemoteADAModelDialogModel(self)
        self.init_url()

    def init_controller(self):
        """Creates the view's controller"""
        self.controller = fetchplugin.FetchRemotePluginDialogController(self)