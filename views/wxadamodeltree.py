"""wxadamodeltree.py - customized version of wxPython's TreeCtrl for the ADA Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from views import wxmodeltree
import wx

class ModelTree(wxmodeltree.ModelTree):
    """ADAModel customized version of wxPython's TreeCtrl, adds
    extra functionality for ADA Toolkit"""

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.root = self.AddRoot("Available Models")
        self.inputdata_lbl = "Input Data"
        self.outputdata_lbl = "Output Data"
        self.indcalls_lbl = "Indication Calls"
        self.indmetrics_lbl = "Indication Metrics"
        self.inddata_lbl = "Indication Data"
        self.parameters_lbl = "Parameters"
        self.settings_lbl = "Settings"

    def add_model(self, ADAModel_tuple):
        """Adds the model ADAModel to the tree"""
        ADAModel_name = ADAModel_tuple[0]
        ADAModel = ADAModel_tuple[1]()
        ADAModel.configure()
        newmodel_branch = self.AppendItem(self.root, ADAModel_name, data=wx.TreeItemData(ADAModel))
        newinputdata_branch = self.AppendItem(newmodel_branch, self.inputdata_lbl)
        for inputdataname, inputdata in sorted(ADAModel.inputdata.iteritems()):
            self.AppendItem(newinputdata_branch, text=inputdataname,
                            data=wx.TreeItemData(inputdata))
        newoutputdata_branch = self.AppendItem(newmodel_branch, self.outputdata_lbl)
        for outputdataname, outputdata in sorted(ADAModel.outputdata.iteritems()):
            self.AppendItem(newoutputdata_branch, text=outputdataname,
                data=wx.TreeItemData(outputdata))
        newindcalls_branch = self.AppendItem(newmodel_branch, self.indcalls_lbl)
        for indcallsname, indcalls in sorted(ADAModel.indcalls.iteritems()):
            self.AppendItem(newindcalls_branch, text=indcallsname,
                data=wx.TreeItemData(indcalls))
        newindmetrics_branch = self.AppendItem(newmodel_branch, self.indmetrics_lbl)
        for indmetricsname, indmetrics in sorted(ADAModel.indmetrics.iteritems()):
            self.AppendItem(newindmetrics_branch, text=indmetricsname,
                data=wx.TreeItemData(indmetrics))
        newinddata_branch = self.AppendItem(newmodel_branch, self.inddata_lbl)
        for inddataname, inddata in sorted(ADAModel.inddata.iteritems()):
            self.AppendItem(newinddata_branch, text=inddataname,
                data=wx.TreeItemData(inddata))
        newparameter_branch = self.AppendItem(newmodel_branch, self.parameters_lbl)
        for parametername, parameter in sorted(ADAModel.params.iteritems()):
            self.AppendItem(newparameter_branch, text=parametername,
                            data=wx.TreeItemData(parameter))
        newsetting_branch = self.AppendItem(newmodel_branch, self.settings_lbl)
        for settingname, setting in sorted(ADAModel.settings.iteritems()):
            self.AppendItem(newsetting_branch, text=settingname,
                            data=wx.TreeItemData(setting))
        self.ExpandAllChildren(newmodel_branch)
        return newmodel_branch

    def get_all_model_items(self):
        """Returns a list of all the ADAModel wxTreeItems in the tree"""
        models = []
        branch, breadcrumb = self.GetFirstChild(self.root)
        while branch.IsOk():
            models.append(branch)
            branch, breadcrumb = self.GetNextChild(branch, breadcrumb)
        return models

    def update_model(self):
        """Updates the currently-selected ADA Model based on the current configuration.
        Walks the tree."""
        model_item = self.selected_model_item()
        if model_item is not None:
            model = self.GetPyData(model_item)
            inputdata = {}
            outputdata = {}
            indcalls = {}
            indmetrics = {}
            inddata = {}
            params = {}
            settings = {}
            branch, breadcrumb = self.GetFirstChild(model_item)
            while branch.IsOk():
                branch_lbl = self.GetItemText(branch)
                branch_dict = self.get_branch(branch)
                if branch_lbl == self.inputdata_lbl:
                    inputdata = branch_dict
                elif branch_lbl == self.outputdata_lbl:
                    outputdata = branch_dict
                elif branch_lbl == self.indcalls_lbl:
                    indcalls = branch_dict
                elif branch_lbl == self.indmetrics_lbl:
                    indmetrics = branch_dict
                elif branch_lbl == self.inddata_lbl:
                    inddata = branch_dict
                elif branch_lbl == self.parameters_lbl:
                    params = branch_dict
                elif branch_lbl == self.settings_lbl:
                    settings = branch_dict
                branch, breadcrumb = self.GetNextChild(branch, breadcrumb)
            model.inputdata = inputdata
            model.outputdata = outputdata
            model.indcalls = indcalls
            model.indmetrics = indmetrics
            model.inddata = inddata
            model.parameters = params
            model.settings = settings

    def selection_is_outputdata(self):
        """Returns True if the current selection is inputdata.  Does not walk the tree."""
        return self.selectionParentLabel() == self.outputdata_lbl

    def selection_is_indcalls(self):
        """Returns True if the current selection is inputdata.  Does not walk the tree."""
        return self.selectionParentLabel() == self.indcalls_lbl

    def selection_is_indmetrics(self):
        """Returns True if the current selection is inputdata.  Does not walk the tree."""
        return self.selectionParentLabel() == self.indmetrics_lbl

    def selection_is_inddata(self):
        """Returns True if the current selection is inputdata.  Does not walk the tree."""
        return self.selectionParentLabel() == self.inddata_lbl

    def selected_outputdata(self):
        """Returns a ModelProperty instance of the currently selected
        outputdata, or None if outputdata isn't selected."""
        outputdata = None
        if self.selection_is_outputdata():
            outputdata = self.get_selected_object()
        return outputdata

    def selected_indcalls(self):
        """Returns a ModelProperty instance of the currently selected
        indcalls, or None if indcalls isn't selected."""
        indcalls = None
        if self.selection_is_indcalls():
            indcalls = self.get_selected_object()
        return indcalls

    def selected_indmetrics(self):
        """Returns a ModelProperty instance of the currently selected
        indmetrics, or None if indmetrics isn't selected."""
        indmetrics = None
        if self.selection_is_indmetrics():
            indmetrics = self.get_selected_object()
        return indmetrics

    def selected_inddata(self):
        """Returns a ModelProperty instance of the currently selected
        inddata, or None if inddata isn't selected."""
        inddata = None
        if self.selection_is_inddata():
            inddata = self.get_selected_object()
        return inddata

class ModelTreeContextMenu(wxmodeltree.ModelTreeContextMenu):
    """Basic right-click popup menu for ModelTree controls."""

    def __init__(self, parent):
        wxmodeltree.ModelTreeContextMenu.__init__(self, parent)