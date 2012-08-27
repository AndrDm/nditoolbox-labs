"""wxadamodeltree.py - customized version of wxPython's TreeCtrl for the ADA Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import wx

class ModelTree(wx.TreeCtrl):
    '''ADAModel customized version of wxPython's TreeCtrl, adds
    extra functionality for ADA Toolkit'''

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE):
        super(ModelTree, self).__init__(parent, id, pos, size, style)
        self.root = self.AddRoot("Available Models")
        self.inputdata_lbl = "Input Data"
        self.outputdata_lbl = "Output Data"
        self.indcalls_lbl = "Indication Calls"
        self.indmetrics_lbl = "Indication Metrics"
        self.inddata_lbl = "Indication Data"
        self.parameters_lbl = "Parameters"
        self.settings_lbl = "Settings"

    def clear(self):
        """Removes all ADAModels"""
        self.DeleteChildren(self.root)

    def add_model(self, ADAModel_tuple):
        '''Adds the model ADAModel to the tree'''
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
        '''Returns a list of all the ADAModel wxTreeItems in the tree'''
        models = []
        branch, breadcrumb = self.GetFirstChild(self.root)
        while branch.IsOk():
            models.append(branch)
            branch, breadcrumb = self.GetNextChild(branch, breadcrumb)
        return models

    def get_all_models(self):
        '''Returns a list of all the ADAModel instances in the tree'''
        return [self.GetItemPyData(model_item) for model_item in self.get_all_model_items()]

    def update_model(self):
        '''Updates the currently-selected ADA Model based on the current configuration.
        Walks the tree.'''
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

    def get_branch(self, branch):
        '''Builds and returns a ModelProperty dict based on the provided branch'''
        branchdict = {}
        leaf, cookie = self.GetFirstChild(branch)
        while leaf.IsOk():
            branchdict[self.GetItemText(leaf)] = self.GetPyData(leaf)
            leaf, cookie = self.GetNextChild(leaf, cookie)
        return branchdict

    def selected_model_item(self):
        '''Returns the wx TreeItem for the currently selected ADAModel.
        Walks the tree up if required.'''
        selection = self.GetSelection()
        model = None
        if selection.IsOk():
            oneup = selection
            while oneup != self.GetRootItem():
                model = oneup
                oneup = self.GetItemParent(oneup)
        return model

    def selected_model_name(self):
        '''Returns the name of the currently selected ADAModel.'''
        selected_model = self.selected_model_item()
        if selected_model is not None:
            return self.GetItemText(selected_model)
        else:
            return None

    def selection_is_root(self):
        '''Returns True if the tree's root is the current selection.'''
        return self.GetSelection() == self.GetRootItem()

    def selection_is_model(self):
        '''Returns True if the current selection is a ADAModel.  Does
        not walk the tree.'''
        selection = self.GetSelection()
        return self.GetItemParent(selection) == self.GetRootItem()

    def selectionParentLabel(self):
        '''Returns the label of the current selection's parent or an
        empty string if no parent (root).'''
        selection = self.GetSelection()
        parent_lbl = ''
        ''' Swallow the assertion exception that arises if when the root's
        selected'''
        try:
            if selection.IsOk():
                parent_lbl = self.GetItemText(self.GetItemParent(selection))
        finally:
            return parent_lbl

    def selection_is_inputdata(self):
        '''Returns True if the current selection is inputdata.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.inputdata_lbl

    def selection_is_outputdata(self):
        '''Returns True if the current selection is inputdata.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.outputdata_lbl

    def selection_is_indcalls(self):
        '''Returns True if the current selection is inputdata.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.indcalls_lbl

    def selection_is_indmetrics(self):
        '''Returns True if the current selection is inputdata.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.indmetrics_lbl

    def selection_is_inddata(self):
        '''Returns True if the current selection is inputdata.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.inddata_lbl

    def selection_is_parameter(self):
        '''Returns True if the current selection is a parameter.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.parameters_lbl

    def selection_is_setting(self):
        '''Returns True if the current selection is a setting.  Does not walk the tree.'''
        return self.selectionParentLabel() == self.settings_lbl

    def get_selected_object(self):
        '''Returns a Python object instance of the current selection.'''
        return self.GetPyData(self.GetSelection())

    def get_model(self):
        '''Returns the selected ADA Model with the current configuration.  Walks the tree.'''
        self.update_model()
        return self.GetPyData(self.selected_model_item())

    def selected_inputdata(self):
        '''Returns a ModelProperty instance of the currently selected
        inputdata, or None if inputdata isn't selected.'''
        inputdata = None
        if self.selection_is_inputdata():
            inputdata = self.get_selected_object()
        return inputdata

    def selected_outputdata(self):
        '''Returns a ModelProperty instance of the currently selected
        outputdata, or None if outputdata isn't selected.'''
        outputdata = None
        if self.selection_is_outputdata():
            outputdata = self.get_selected_object()
        return outputdata

    def selected_indcalls(self):
        '''Returns a ModelProperty instance of the currently selected
        indcalls, or None if indcalls isn't selected.'''
        indcalls = None
        if self.selection_is_indcalls():
            indcalls = self.get_selected_object()
        return indcalls

    def selected_indmetrics(self):
        '''Returns a ModelProperty instance of the currently selected
        indmetrics, or None if indmetrics isn't selected.'''
        indmetrics = None
        if self.selection_is_indmetrics():
            indmetrics = self.get_selected_object()
        return indmetrics

    def selected_inddata(self):
        '''Returns a ModelProperty instance of the currently selected
        inddata, or None if inddata isn't selected.'''
        inddata = None
        if self.selection_is_inddata():
            inddata = self.get_selected_object()
        return inddata

    def selected_parameter(self):
        '''Returns a ModelProperty instance of the currently selected
        parameter, or None if a parameter isn't selected.'''
        param = None
        if self.selection_is_parameter():
            param = self.get_selected_object()
        return param

    def selected_setting(self):
        '''Returns a ModelProperty instance of the currently selected
        setting, or None if a setting isn't selected.'''
        setting = None
        if self.selection_is_setting():
            setting = self.get_selected_object()
        return setting

class ModelTreeContextMenu(wx.Menu):
    '''Basic right-click popup menu for ModelTree controls.'''

    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.parent = parent
        self.controller = self.parent.controller
        self.tree = self.parent.modeltree
        '''Contextual menu is based on what type of item is selected'''
        if self.tree.selection_is_root():
            self.generate_rootmenu()
        if self.tree.selection_is_model():
            self.generate_modelmenu()
        if self.tree.selection_is_inputdata():
            self.generate_inputdatamenu()

    def generate_rootmenu(self):
        '''Generate a menu when right-clicking the root'''
        add_model = wx.MenuItem(self, wx.NewId(), 'Install Model')
        self.AppendItem(add_model)
        self.Bind(wx.EVT_MENU, self.controller.on_install_model, id=add_model.GetId())

    def generate_modelmenu(self):
        '''Contextual menu for right-clicking on a model'''
        save_model = wx.MenuItem(self, wx.NewId(), "Save This Model")
        self.AppendItem(save_model)
        self.Bind(wx.EVT_MENU, self.controller.on_save_model, id=save_model.GetId())
        del_model = wx.MenuItem(self, wx.NewId(), 'Delete This Model')
        self.AppendItem(del_model)
        self.Bind(wx.EVT_MENU, self.controller.on_delete_model, id=del_model.GetId())

    def generate_inputdatamenu(self):
        '''Contextual menu for right-clicking an InputData item'''
        edit_sheet = wx.MenuItem(self, wx.NewId(), 'Edit Worksheet')
        self.AppendItem(edit_sheet)
        self.Bind(wx.EVT_MENU, self.controller.on_edit_inputdata, id=edit_sheet.GetId())
        choose_file = wx.MenuItem(self, wx.NewId(), 'Choose File Location...')
        self.AppendItem(choose_file)
        self.Bind(wx.EVT_MENU, self.controller.on_choose_inputdata, id=choose_file.GetId())