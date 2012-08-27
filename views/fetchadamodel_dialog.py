"""fetchadamodel_dialog.py - wxPython dialogs for installing ADAModel archives

Chris R. Coughlin (TRI/Austin, Inc.) and John C. Aldrin (Computational Tools)
"""

__author__ = 'Chris R. Coughlin'

from views import fetchplugin_dialog
from controllers import fetchadamodel_dialog_ctrl

class FetchADAModelDialog(fetchplugin_dialog.FetchPluginDialog):
    """wxPython dialog for installing ADA Models from the local filesystem"""

    def __init__(self, parent, plugin_path=None):
        self.plugin_type = "ADA Model"
        super(FetchADAModelDialog, self).__init__(parent, plugin_path, self.plugin_type)

    def init_controller(self):
        """Creates the view's controller"""
        self.controller = fetchadamodel_dialog_ctrl.FetchADAModelDialogController(self)


class FetchRemoteADAModelDialog(fetchplugin_dialog.FetchRemotePluginDialog):
    """wxPython dialog for downloading and installing ADA Models"""

    def __init__(self, parent):
        self.plugin_type = "ADA Model"
        super(FetchRemoteADAModelDialog, self).__init__(parent, self.plugin_type)

    def init_controller(self):
        """Creates the view's controller"""
        self.controller = fetchadamodel_dialog_ctrl.FetchRemoteADAModelDialogController(self)