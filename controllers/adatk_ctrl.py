"""adatk_ctrl.py - controller for the ADA Toolkit

Chris R. Coughlin (TRI/Austin, Inc.) and John C. Aldrin (Computational Tools)
"""

__author__ = 'Chris R. Coughlin and John C. Aldrin'

from models.adatk_model import ADAWindowModel
from models import workerthread
from models import file_finder
from controllers import pathfinder
from views import dialogs
from views import fetchadamodel_dialog
from views.wxdirtreectrl import DirTreeCtrl
import wx
import numpy as np
import Queue

class ADAWindowController(object):
    """Controller for the ADAWindow UI"""

    def __init__(self, view):
        self.view = view
        self.model = ADAWindowModel(self)
        self.indcombo_des = None
        self.indcombo_txt = None

    def get_models(self):
        """Retrieves the list of ADAModels
        and populates the TreeCtrl"""
        ada_models = self.model.load_models()
        for model in ada_models:
            self.view.modeltree.add_model(model)

    # Event Handlers
    def on_quit(self, evt):
        """Handles Close Window request"""
        self.view.close()

    def on_download_model(self, evt):
        """Handles request to download and install a plugin"""
        dlg = fetchadamodel_dialog.FetchRemoteADAModelDialog(parent=self.view)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                dlg.install_plugin()
                self.view.modeltree.clear()
                self.get_models()
            except Exception as err:
                err_msg = "{0}".format(err)
                err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                           caption="Unable To Install ADA Model",
                                           style=wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
        dlg.Destroy()

    def on_install_model(self, evt):
        """Handles request to install a local ADA Model"""
        file_dlg = wx.FileDialog(parent=self.view,
                                 message="Please select a ADA Model archive to install.",
                                 wildcard="ZIP files (*.zip)|*.zip|All files (*.*)|*.*")
        if file_dlg.ShowModal() == wx.ID_OK:
            dlg = fetchadamodel_dialog.FetchADAModelDialog(parent=self.view,
                                                           plugin_path=file_dlg.GetPath())
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    dlg.install_plugin()
                    self.view.modeltree.clear()
                    self.get_models()
                except Exception as err:
                    err_msg = "{0}".format(err)
                    err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                               caption="Unable To Install ADA Model",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
            dlg.Destroy()
        file_dlg.Destroy()

    def on_delete_model(self, evt):
        """Handles request to delete a model"""
        # Placeholder for now
        delmodel_dlg = wx.MessageDialog(self.view, caption="Remove A ADA Model",
                                        message="This feature not yet implemented.\nPlease "\
                                                "contact TRI for assistance."
                                        ,
                                        style=wx.OK | wx.ICON_INFORMATION)
        delmodel_dlg.ShowModal()
        delmodel_dlg.Destroy()

    def on_about(self, evt):
        """Handles request to show About dialog"""
        # Placeholder for now
        about_dlg = wx.MessageDialog(self.view, caption="About ADAToolkit",
                                     message="This is the Probability Of Detection Toolkit",
                                     style=wx.OK | wx.ICON_INFORMATION)
        about_dlg.ShowModal()
        about_dlg.Destroy()

    def on_help(self, evt):
        """Handles request to show Help information"""
        # Placeholder for now
        help_dlg = wx.MessageDialog(self.view, caption="ADAToolkit Help",
                                    message="This feature not yet implemented.\nPlease contact "\
                                            "TRI for assistance."
                                    ,
                                    style=wx.OK | wx.ICON_INFORMATION)
        help_dlg.ShowModal()
        help_dlg.Destroy()

    def on_selection_change(self, evt):
        """Handles selection change event in ModelTree -
        updates ModelProperty Editor"""
        item = evt.GetItem()
        if item:
            self.refresh_mpgrid(item)
        evt.Skip()

    def refresh_mpgrid(self, item):
        """Updates the ModelProperties Grid with the specified
        ModelTree item."""
        selected_obj = self.view.modeltree.GetItemPyData(item)
        if isinstance(selected_obj, dict):
            self.view.mp_lbl.SetLabel(self.view.modeltree.selectionParentLabel())
            self.view.mp_grid.ClearGrid()
            props = selected_obj.keys()
            self.view.mp_grid.SetNumberRows(len(props))
            row = 0
            for prop in props:
                self.view.mp_grid.SetCellValue(row, 0, prop)
                self.view.mp_grid.SetCellValue(row, 1, str(selected_obj.get(prop)))
                row += 1

    def refresh_rpgrid(self, prop_nam, prop_val):
        """Updates the Run Conditions (Properties) Grid"""
        self.view.rp_grid.ClearGrid()
        self.view.rp_grid.SetNumberRows(len(prop_nam))
        row = 0
        for idx in range(len(prop_nam)):
            self.view.rp_grid.SetCellValue(row, 0, prop_nam[idx])
            self.view.rp_grid.SetCellValue(row, 1, prop_val[idx])
            row += 1

    def on_modeltree_change(self, evt):
        """Handles changes in the ModelTree - updates ModelProperty Editor"""
        self.on_selection_change(evt)

    def on_right_click_modeltree(self, evt):
        """Handles right-click event in the ModelTree"""
        click_pos = evt.GetPosition()
        item, flags = self.view.modeltree.HitTest(click_pos)
        if item:
            self.view.modeltree.SelectItem(item)
            # Aug-30-2012 [crc] - disable context menu
            # until input/output data file issue resolved (ADA models
            # spec multiple file inputs/outputs that aren't files)
            #self.view.tree_popup(click_pos)

    def on_edit_inputdata(self, evt):
        """Handles request to load input data into worksheet"""
        input_data = self.view.modeltree.selected_inputdata()
        if input_data is not None:
            if input_data['filetype'].lower() == 'csv':
                try:
                    data = self.model.load_data(input_data['filename'])
                    self.populate_spreadsheet(self.view.input_grid, data)
                except IOError as err:
                    err_dlg = wx.MessageDialog(self.view, caption="Failed To Read File",
                                               message=str(err), style=wx.OK | wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()

    def on_choose_inputdata(self, evt):
        """Handles request to set input data file"""
        selected_input_data = self.view.modeltree.GetSelection()
        if selected_input_data.IsOk():
            file_dlg = wx.FileDialog(self.view, message="Please select a CSV file",
                                     wildcard="CSV files (*.csv)|*.csv|Text Files (*.txt)|*"\
                                              ".txt|All Files (*.*)|*.*"
                                     ,
                                     style=wx.FD_OPEN)
            if file_dlg.ShowModal() == wx.ID_OK:
                inputdata_item = self.view.modeltree.GetItemPyData(selected_input_data)
                inputdata_item['filename'] = file_dlg.GetPath()
                self.view.modeltree.SetItemPyData(selected_input_data, inputdata_item)
                self.view.modeltree.SelectItem(selected_input_data)
                self.refresh_mpgrid(selected_input_data)

    def on_grid_cellselected(self, evt):
        """Handles selection change event in output_grid """
        #int_r = evt.Row
        int_c = evt.Col
        self.view.txtoutput_tc.Clear()
        # check if self.indcombo_des was created
        if self.indcombo_des is not None:
            self.view.txtoutput_tc.WriteText(self.indcombo_des[int_c])
        else:
            self.view.txtoutput_tc.WriteText(str(int_c))
    #
        evt.Skip()

    def on_grid2_cellselected(self, evt):
        """Handles selection change event in output_grid """
        int_r = evt.Row
        int_c = evt.Col
        self.view.txtind.Clear()
        self.view.txtind.WriteText(str(int_r))
        model = self.view.modeltree.get_model()
        model.idx_localplot = int_r
        evt.Skip()
        self.on_lplistbox1_change(evt)
        self.on_lplistbox2_change(evt)

    def on_sheet_tool_click(self, evt):
        """Handles toolbar button clicks in the spreadsheet -
        currently supports Open File (id=20) and Save File (id=30)."""
        if evt.GetId() == 20: # Open File
            file_dlg = wx.FileDialog(self.view, message="Please select a CSV file",
                                     wildcard="CSV files (*.csv)|*.csv|Text Files (*.txt)|*"\
                                              ".txt|All Files (*.*)|*.*"
                                     ,
                                     style=wx.FD_OPEN)
            if file_dlg.ShowModal() == wx.ID_OK:
                try:
                    data = self.model.load_data(file_dlg.GetPath())
                    if data is not None:
                        self.populate_spreadsheet(grid, data)
                    else:
                        raise IOError("File not recognized as CSV.")
                except Exception as err:
                    if str(err) is None:
                        msg = "An unknown error occurred attempting to read the file."
                    else:
                        msg = "An error occurred attempting to read the file:\n\n{0}".format(
                            str(err))
                    err_dlg = wx.MessageDialog(self.view, caption="Failed To Read File",
                                               message=msg, style=wx.OK | wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
        elif evt.GetId() == 30: # Save File
            save_file_dlg = wx.FileDialog(self.view, message="Please specify an output filename",
                                          defaultDir=pathfinder.adamodels_path(),
                                          wildcard="CSV files (*.csv)|*.csv|Text Files (*.txt)|*"\
                                                   ".txt|All Files (*.*)|*.*"
                                          ,
                                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if save_file_dlg.ShowModal() == wx.ID_OK:
                grid = self.get_active_grid()
                grid.WriteCSV(save_file_dlg.GetPath())
            save_file_dlg.Destroy()

    def get_active_grid(self):
        """Returns the currently-selected Spreadsheet control from the view"""
        grid = None
        active_page = self.view.spreadsheet_nb.GetSelection()
        if active_page == 1:
            grid = self.view.input_grid
        elif active_page == 2:
            grid = self.view.output_grid
        elif active_page == 3:
            grid = self.view.output_grid2
        return grid

    def on_property_change(self, evt):
        """Handles changes in ModelProperty Editor - ModelTree updated
        with new values."""
        click_pos = evt.GetPosition()
        item = self.view.mp_grid.HitTest(click_pos)
        if item:
            property_name = self.view.mp_grid.GetCellValue(evt.GetRow(), 0)
            property_value = self.view.mp_grid.GetCellValue(evt.GetRow(), 1)
            selected_property = self.view.modeltree.GetSelection()
            if selected_property.IsOk() and selected_property != self.view.modeltree.GetRootItem():
                self.view.modeltree.GetItemPyData(selected_property)[property_name] =\
                property_value

    def on_gplistbox_change(self, evt):
        """Handles selection change event for self.gp_listbox """
        #idx = self.view.gp_listbox.GetSelection()
        #self.view.txtoutput_tc.Clear()
        #self.on_testrunmodel(evt)
        try:
            model = self.view.modeltree.get_model()
            if model.res_outputdata is not None:
                # Get gp_listbox seleciton for plot0
                idx = self.view.gp_listbox.GetSelection()
                # Create plot0 (either C-scan or A-scan)
                Nr, Nc = model.res_outputdata[idx].shape
                if Nr > 3:
                    xlims = self.view.axes0.get_xlim()
                    ylims = self.view.axes0.get_ylim()
                    #xlims = self.view.axes0.xlims
                    #ylims = self.view.axes0.ylims
                    #
                    self.view.axes0.clear()
                    self.view.figure0.clear()  #in case there are extra axes like colorbars
                    self.view.axes0 = self.view.figure0.add_subplot(111, navigate=True)
                    cax = self.view.axes0.imshow(model.res_outputdata[idx])
                    #
                    Nr1, Nc1 = model._data.shape
                    for idx in range(Nr1):
                        xc = model._data[idx,1]
                        yc = model._data[idx,2]
                        tc = str(idx+1)
                        self.view.axes0.text(xc,yc,tc)
                    #
                    self.view.colorbar = self.view.figure0.colorbar(cax)
                    self.view.axes0.set_xlabel('x')
                    self.view.axes0.set_ylabel('y')
                    self.view.plot0_panel.Show()
                    #
                    #self.view.axes0.xlims = self.view.axes0.get_xlim()
                    #self.view.axes0.ylims = self.view.axes0.get_ylim()
                    #
                    xsum = xlims[0]+xlims[1]
                    if xsum > 1:
                        if ylims[0] > ylims[1]:
                            self.view.axes0.set_xlim(xlims)
                            self.view.axes0.set_ylim(ylims)

                    #
                    self.refresh_plot0()
                    #
                    #xlims = self.view.axes0.get_xlim()
                    #ylims = self.view.axes0.get_ylim()
                else:
                    self.view.axes0.clear()
                    self.view.figure0.clear() #in case there are extra axes like colorbars
                    self.view.axes0 = self.view.figure0.add_subplot(111, navigate=True)
                    M = model.res_outputdata[idx]
                    self.view.axes0.plot(M[0,:].copy(), M[1,:].copy(), 'k-')
                    self.view.axes0.set_xlabel("t (steps)")
                    self.view.axes0.set_ylabel("V ()")
                    self.view.plot0_panel.Show()
                    self.refresh_plot0()
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_gpreplot_change(self, evt):
        """Handles selection change event for self.gp_listbox """
        #idx = self.view.gp_listbox.GetSelection()
        #self.view.txtoutput_tc.Clear()
        #self.on_testrunmodel(evt)
        try:
            model = self.view.modeltree.get_model()
            if model.res_outputdata is not None:
                # Get lp_listbox seleciton for plot1
                idx = self.view.gp_listbox.GetSelection()
                # Create plot0 (either C-scan or A-scan)
                Nr, Nc = model.res_outputdata[idx].shape
                if Nr >= 3:
                    #self.view.axes1.clear()
                    #self.view.figure1.clear()  #in case there are extra axes like colorbars
                    xlims = self.view.axes0.get_xlim()
                    ylims = self.view.axes0.get_ylim()
                    #
                    self.view.axes0.clear()
                    self.view.figure0.clear()  #in case there are extra axes like colorbars
                    self.view.axes0 = self.view.figure0.add_subplot(111, navigate=True)
                    #
                    a0 = self.view.plot0_txt0.GetValue()
                    i1 = int(a0)
                    a1 = self.view.plot0_txt1.GetValue()
                    i2 = int(a1)
                    #
                    self.view.axes0 = self.view.figure0.add_subplot(111, navigate=True)
                    cax = self.view.axes0.imshow(model.res_outputdata[idx], vmin = i1, vmax = i2)
                    #
                    Nr1, Nc1 = model._data.shape
                    for idx in range(Nr1):
                        xc = model._data[idx,1]
                        yc = model._data[idx,2]
                        tc = str(idx+1)
                        self.view.axes0.text(xc,yc,tc)
                        #
                    self.view.colorbar = self.view.figure0.colorbar(cax)
                    self.view.axes0.set_xlabel('x')
                    self.view.axes0.set_ylabel('y')
                    self.view.plot0_panel.Show()
                    #
                    xsum = xlims[0]+xlims[1]
                    if xsum > 1:
                        self.view.axes0.set_xlim(xlims)
                        self.view.axes0.set_ylim(ylims)
                        #
                    self.refresh_plot0()
                    #
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()


    def on_lplistbox1_change(self, evt):
        """Handles selection change event for self.gp_listbox """
        #idx = self.view.gp_listbox.GetSelection()
        #self.view.txtoutput_tc.Clear()
        #self.on_testrunmodel(evt)
        try:
            model = self.view.modeltree.get_model()
            i_row = model.idx_localplot
            if model.res_inddata is not None:
                # Get lp_listbox seleciton for plot1
                idx = self.view.lp_listbox1.GetSelection()
                # Create plot0 (either C-scan or A-scan)
                Nr, Nc = model.res_inddata[idx][i_row].shape
                if Nr >= 3:
                    self.view.axes1.clear()
                    self.view.figure1.clear()  #in case there are extra axes like colorbars
                    self.view.axes1 = self.view.figure1.add_subplot(111, navigate=True)
                    cax = self.view.axes1.imshow(model.res_inddata[idx][i_row])
                    self.view.colorbar = self.view.figure1.colorbar(cax)
                    self.view.axes1.set_xlabel('x')
                    self.view.axes1.set_ylabel('y')
                    self.view.plot_panel.Show()
                    self.refresh_plots()
                else:
                    self.view.axes1.clear()
                    self.view.figure1.clear() #in case there are extra axes like colorbars
                    self.view.axes1 = self.view.figure1.add_subplot(111, navigate=True)
                    M = model.res_inddata[idx][i_row]
                    self.view.axes1.plot(M[0,:].copy(), M[1,:].copy(), 'k-')
                    self.view.axes1.set_xlabel("t (steps)")
                    self.view.axes1.set_ylabel("V ()")
                    self.view.plot_panel.Show()
                    self.refresh_plots()
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_lplistbox2_change(self, evt):
        try:
            model = self.view.modeltree.get_model()
            i_row = model.idx_localplot
            if model.res_inddata is not None:
                # Get lp_listbox seleciton for plot1
                idx = self.view.lp_listbox2.GetSelection()
                # Create plot0 (either C-scan or A-scan)
                Nr, Nc = model.res_inddata[idx][i_row].shape
                if Nr >= 3:
                    self.view.axes2.clear()
                    self.view.figure2.clear()  #in case there are extra axes like colorbars
                    self.view.axes2 = self.view.figure2.add_subplot(111, navigate=True)
                    cax = self.view.axes2.imshow(model.res_inddata[idx][i_row])
                    self.view.colorbar = self.view.figure2.colorbar(cax)
                    self.view.axes2.set_xlabel('x')
                    self.view.axes2.set_ylabel('y')
                    self.view.plot_panel.Show()
                    self.refresh_plots()
                else:
                    self.view.axes2.clear()
                    self.view.figure2.clear() #in case there are extra axes like colorbars
                    self.view.axes2 = self.view.figure2.add_subplot(111, navigate=True)
                    M = model.res_inddata[idx][i_row]
                    self.view.axes2.plot(M[0,:].copy(), M[1,:].copy(), 'k-')
                    self.view.axes2.set_xlabel("t (steps)")
                    self.view.axes2.set_ylabel("V ()")
                    self.view.plot_panel.Show()
                    self.refresh_plots()
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_save_model(self, evt):
        """Handles request to store ADA Model configuration changes to disk"""
        try:
            model = self.view.modeltree.get_model()
            if model is not None:
                model.save_configuration()
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                                       message="Please select a ADA Model.",
                                       style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_runmodel(self, evt):
        """Handles request to execute current ADA Model"""
        try:
            model = self.view.modeltree.get_model()
            if model is not None:
                self.run_model(model)
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                                       message="Please select a ADA Model.",
                                       style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_testrunmodel(self, evt):
        """Handles request to execute current ADA Model"""
        try:
            #model = self.view.modeltree.get_model()
            # Create dummy data for testing
            Nx = 400
            Ny = 300
            Nt = 1000
            x = np.array([np.arange(0, Nx, 1)])
            y = np.array([np.arange(0, Ny, 1)])
            t = np.array([np.arange(0, Nt, 1)])
            ascan = np.sin(0.2*t)*np.exp(-0.02*(t-100.0*np.ones((1,Nt)))**2.0)+0.05*np.random.rand(1,Nt)
            ta = np.ones((2,Nt))
            for idx in range(Nt):
                tmp = t[0,idx]
                ta[0,idx] = t[0,idx]
                ta[1,idx] = ascan[0,idx]
            xx, yy = np.mgrid[0:Nx,0:Ny]
            self.res_outputdata = []
            # Store in res_outputdata
            self.res_outputdata.append(10*np.random.rand(Nx,Ny))
            self.res_outputdata.append(1*np.random.rand(Nx,Ny)+0.01*xx)
            self.res_outputdata.append(1*np.random.rand(Nx,Ny)+0.01*xx+0.01*yy)
            self.res_outputdata.append(ta)
            # Get gp_listbox seleciton for plot0
            idx = self.view.gp_listbox.GetSelection()
            # Create plot0 (either C-scan or A-scan)
            Nr, Nc = self.res_outputdata[idx].shape
            if Nr > 3:
                self.view.axes0.clear()
                self.view.figure0.clear()  #in case there are extra axes like colorbars
                self.view.axes0 = self.view.figure0.add_subplot(111, navigate=True)
                cax = self.view.axes0.imshow(self.res_outputdata[idx])
                self.view.colorbar = self.view.figure0.colorbar(cax)
                self.view.axes0.set_xlabel('x')
                self.view.axes0.set_ylabel('y')
                self.view.plot0_panel.Show()
                self.refresh_plot0()
            else:
                self.view.axes0.clear()
                self.view.figure0.clear() #in case there are extra axes like colorbars
                self.view.axes0 = self.view.figure0.add_subplot(111, navigate=True)
                M = self.res_outputdata[idx]
                self.view.axes0.plot(M[0,:].copy(), M[1,:].copy(), 'k-')
                self.view.axes0.set_xlabel("t (steps)")
                self.view.axes0.set_ylabel("V ()")
                self.view.plot0_panel.Show()
                self.refresh_plot0()
        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_testrunmodel2(self, evt):
        """Handles request to execute current ADA Model"""
        try:
            model = self.view.modeltree.get_model()
            # Create dummy data for testing

        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_extramodel(self, evt):
        """Test code for extracting data from the ADA model"""
        try:
            model = self.view.modeltree.get_model()
            #
            ind_names = []
            for indmetricsname, indmetrics2 in sorted(model.indmetrics.iteritems()):
                print("\t{0}".format(indmetricsname))
                ind_names.append(indmetricsname)
            #self.AppendItem(newindmetrics_branch, text=indmetricsname,
            #        data=wx.TreeItemData(indmetrics))
            #
            ind_names_txt = []
            ind_names_idx = []
            for indmetricsname, indmetrics2 in sorted(model.indmetrics.iteritems()):
                ind_names_txt.append(indmetrics2['name'])
                ind_names_idx.append(indmetrics2['index'])
                #
            tmplist = model.indmetrics
            for key, value in model.indmetrics.iteritems():
                print("\t{0}={1}".format(key, value))
            #
            #sorted_list = [x for x in model.indmetrics.iteritems()]
            ############################################################
            names_nam = []
            names_idx = []
            names_txt = []
            names_val = []
            names_dim = []
            names_des = []
            for ikey, ivalues in sorted(model.outputdata.iteritems()):
                names_nam.append(ikey)
                names_txt.append(ivalues['name'])
                names_idx.append(ivalues['index'])
                names_val.append(ivalues['value'])
                names_dim.append(ivalues['dimension'])
                names_des.append(ivalues['description'])
            Ni = len(names_idx)
            idp = 0
            outputpara_nam = []
            outputpara_idx = []
            outputpara_txt = []
            outputpara_val = []
            outputpara_des = []
            idf = 0
            outputdata_nam = []
            outputdata_idx = []
            outputdata_txt = []
            outputdata_val = []
            outputdata_dim = []
            outputdata_des = []
            for idx in range(len(names_idx)):
                if names_dim[idx] == '0':
                    idp = idp + 1
                    outputpara_nam.append(names_nam[idx])
                    outputpara_idx.append(names_idx[idx])
                    outputpara_txt.append(names_txt[idx])
                    outputpara_val.append(names_val[idx])
                    outputpara_des.append(names_des[idx])
                else:
                    idf = idf + 1
                    outputdata_nam.append(names_nam[idx])
                    outputdata_idx.append(names_idx[idx])
                    outputdata_txt.append(names_txt[idx])
                    outputdata_val.append(names_val[idx])
                    outputdata_des.append(names_des[idx])
            Np = idp
            Nf = idf
            self.refresh_rpgrid(outputpara_txt, outputpara_val)
            self.view.gp_listbox.Clear()
            self.view.gp_listbox.InsertItems(outputdata_des,0)
            #
            n_gp = 0
            for ikey, ivalues in sorted(model.settings.iteritems()):
                if ikey == 'Primary Results Plot':
                    n_gp = int(ivalues['value'])
            self.view.gp_listbox.SetSelection(n_gp)
            # need to store order and dimension for global plotting
            ############################################################
            names_nam = []
            names_idx = []
            names_txt = []
            names_val = []
            names_dim = []
            names_des = []
            for ikey, ivalues in sorted(model.inddata.iteritems()):
                names_nam.append(ikey)
                names_txt.append(ivalues['name'])
                names_idx.append(ivalues['index'])
                names_val.append(ivalues['value'])
                names_dim.append(ivalues['dimension'])
                names_des.append(ivalues['description'])
            Ni = len(names_idx)
            inddata_idx = [' ']*Ni
            inddata_nam = [' ']*Ni
            inddata_txt = [' ']*Ni
            inddata_val = [' ']*Ni
            inddata_dim = [' ']*Ni
            inddata_des = [' ']*Ni
            for idx in range(len(names_idx)):
                idx2 = int(names_idx[idx])-1
                inddata_nam[idx2] = names_nam[idx]
                inddata_txt[idx2] = names_txt[idx]
                inddata_val[idx2] = names_val[idx]
                inddata_dim[idx2] = names_dim[idx]
                inddata_des[idx2] = names_des[idx]
            self.view.lp_listbox1.Clear()
            self.view.lp_listbox1.InsertItems(inddata_des,0)
            self.view.lp_listbox2.Clear()
            self.view.lp_listbox2.InsertItems(inddata_des,0)
            #
            n_lp1 = 0
            n_lp2 = 1
            for ikey, ivalues in sorted(model.settings.iteritems()):
                if ikey == 'Indication Results Plot 1':
                    n_lp1 = int(ivalues['value'])
                if ikey == 'Indication Results Plot 2':
                    n_lp2 = int(ivalues['value'])
            self.view.lp_listbox1.SetSelection(n_lp1)
            self.view.lp_listbox2.SetSelection(n_lp2)
            # need to store order and dimension for local plotting
            ############################################################
            self.view.txtind.Clear()
            self.view.txtind.WriteText("Test Call Description")
            self.view.txtoutput_tc.Clear()
            self.view.txtoutput_tc.WriteText("Test Status")
            #
            self.populate_paraspreadsheet_headers(self.view.input_grid)

        except ValueError: # No model selected
            err_dlg = wx.MessageDialog(self.view, caption="No Model Selected",
                message="Please select a ADA Model.",
                style=wx.OK | wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()

    def on_add_folder(self, evt):
        """Handles request to add a folder and its subfolders to the tree"""
        dir_dlg = wx.DirDialog(self.view, "Please select a folder.")
        if dir_dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()
            self.view.dirtree.add_folder(dir_dlg.GetPath())
            wx.EndBusyCursor()

    def on_remove_folder(self, evt):
        """Handles request to remove selected folder"""
        self.view.dirtree.remove_folder()

    def on_folder_list(self, evt):
        """Handles request to list folders"""
        folders = self.view.dirtree.selected_folders()
        if len(folders) == 0:
            folders = self.view.dirtree.get_folders()
        self.view.listfolders_lb.Set(sorted(folders))

    def on_search_files(self, evt):
        """Handles request to search selected folder(s) for files matching specified file extension."""
        self.view.listfiles_lb.Clear()
        wx.BeginBusyCursor()

        search_folders = [self.view.listfolders_lb.GetString(fldr) for fldr in self.view.listfolders_lb.GetSelections()]
        if len(search_folders) == 0:
            search_folders = self.view.dirtree.get_folders()
        for folder in sorted(search_folders):
            ext = self.view.file_cb.GetStringSelection()
            f = file_finder.exact_match(ext.lower(), folder)
            self.view.listfiles_lb.AppendItems(sorted(f))
        wx.EndBusyCursor()

    def run_model(self, model_instance):
        """Runs the specified ADA Model instance in a separate thread."""
        exception_queue = Queue.Queue()
        model_thd = workerthread.WorkerThread(exception_queue=exception_queue,
                                              target=model_instance.run)
        model_thd.start()
        progress_dlg = dialogs.progressDialog(dlg_title="Running ADA Model",
                                              dlg_msg="Please wait, running ADA Model...")
        while True:
            model_thd.join(0.125)
            progress_dlg.update()
            if not model_thd.is_alive():
                try:
                    exc_type, exc = exception_queue.get(block=False)
                    err_msg = "An error occurred while running the ADA Model:\n{0}".format(exc)
                    err_dlg = wx.MessageDialog(self.view.parent, message=err_msg,
                                               caption="Error In ADA Model Execution",
                                               style=wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return
                except Queue.Empty:
                    # No errors occurred, continue processing
                    model_instance.plot0(self.view.axes0, self.view.figure0)
                    model_instance.plot1(self.view.axes1, self.view.figure1)
                    model_instance.plot2(self.view.axes2, self.view.figure2)
                    if model_instance.data is not None: # Model returned data to display
                        try:
                            self.populate_spreadsheet(self.view.output_grid, model_instance.data)
                            self.populate_spreadsheet(self.view.output_grid2, model_instance.data)
                            self.populate_outputparaspreadsheet()
                            self.view.spreadsheet_nb.ChangeSelection(self.view.res_summary_page)
                        except MemoryError: # File too large to load
                            err_msg = "The file is too large to load."
                            err_dlg = wx.MessageDialog(self.view, message=err_msg,
                                                       caption="Unable To Preview Data",
                                                       style=wx.ICON_ERROR)
                            err_dlg.ShowModal()
                            err_dlg.Destroy()
                #if model_instance.params is not None: # Model return output text to display
                #    for key, value in model_instance.settings.iteritems():
                #        self.view.txtoutput_tc.WriteText(model_instance.results)
                    if model_instance.results is not None: # Model return output text to display
                        self.view.txtoutput_tc.Clear()
                        self.view.txtoutput_tc.WriteText(model_instance.results)
                    self.refresh_plots()
                    self.refresh_plot0()
                    break
                finally:
                    progress_dlg.close()
            wx.GetApp().Yield(True)

    def refresh_plot0(self):
        """Forces update to the plots (required after some plotting commands)"""
        self.view.canvas0.draw()

    def refresh_plots(self):
        """Forces update to the plots (required after some plotting commands)"""
        self.view.canvas1.draw()
        self.view.canvas2.draw()

    def populate_spreadsheet(self, spreadsheet_ctrl, data_array):
        """Clears the specified wxSpreadSheet instance and fills with
        the contents of the NumPy data_array."""
        spreadsheet_ctrl.ClearGrid()
        spreadsheet_ctrl.SetNumberRows(0)
        spreadsheet_ctrl.SetNumberCols(0)
        rownum = 0
        if data_array.ndim == 2:
            num_rows = data_array.shape[0]
            for row in range(num_rows):
                spreadsheet_ctrl.AppendRows(1)
                numcols = data_array[row].size
                if spreadsheet_ctrl.GetNumberCols() < numcols:
                    spreadsheet_ctrl.SetNumberCols(numcols)
                colnum = 0
                for cell in data_array[row]:
                    spreadsheet_ctrl.SetCellValue(rownum, colnum, str(cell))
                    spreadsheet_ctrl.SetCellValue(rownum, colnum, "{0:.2f}".format(cell))
                    colnum += 1
                rownum += 1
        elif data_array.ndim == 1:
            spreadsheet_ctrl.SetNumberCols(1)
            for el in data_array:
                spreadsheet_ctrl.AppendRows(1)
                #spreadsheet_ctrl.SetCellValue(rownum, 0, "{0:.2f}".format(el))
                rownum += 1
        self.populate_spreadsheet_headers(spreadsheet_ctrl)

    def populate_spreadsheet_headers(self, spreadsheet_ctrl):
        """Get labels from model and add to headers of columns."""
        model = self.view.modeltree.get_model()
        names_txt = []
        names_idx = []
        names_des = []
        for indmetricsname, indmetrics2 in sorted(model.indcalls.iteritems()):
            names_txt.append(indmetrics2['name'])
            names_idx.append(indmetrics2['index'])
            names_des.append(indmetrics2['description'])
        indcall_txt = [' ']*len(names_idx)
        indcall_des = [' ']*len(names_idx)
        for idx in range(len(names_idx)):
            idx2 = int(names_idx[idx])-1
            indcall_txt[idx2] = names_txt[idx]
            indcall_des[idx2] = names_des[idx]
        #
        names_txt = []
        names_idx = []
        names_des = []
        for indmetricsname, indmetrics2 in sorted(model.indmetrics.iteritems()):
            names_txt.append(indmetrics2['name'])
            names_idx.append(indmetrics2['index'])
            names_des.append(indmetrics2['description'])
        indmetric_txt = [' ']*len(names_idx)
        indmetric_des = [' ']*len(names_idx)
        for idx in range(len(names_idx)):
            idx2 = int(names_idx[idx])-1
            indmetric_txt[idx2] = names_txt[idx]
            indmetric_des[idx2] = names_des[idx]
        #
        self.indcombo_txt = indcall_txt + indmetric_txt
        self.indcombo_des = indcall_des + indmetric_des
        for row in range(len(self.indcombo_txt)):
            spreadsheet_ctrl.SetColLabelValue(row,self.indcombo_txt[row])

    def populate_outputparaspreadsheet(self):
        #
        model = self.view.modeltree.get_model()
        #
        names_nam = []
        names_idx = []
        names_txt = []
        names_val = []
        names_dim = []
        names_des = []
        for ikey, ivalues in sorted(model.outputdata.iteritems()):
            names_nam.append(ikey)
            names_txt.append(ivalues['name'])
            names_idx.append(ivalues['index'])
            names_val.append(ivalues['value'])
            names_dim.append(ivalues['dimension'])
            names_des.append(ivalues['description'])
        Ni = len(names_idx)
        idp = 0
        outputpara_nam = []
        outputpara_idx = []
        outputpara_txt = []
        outputpara_val = []
        outputpara_des = []
        idf = 0
        outputdata_nam = []
        outputdata_idx = []
        outputdata_txt = []
        outputdata_val = []
        outputdata_dim = []
        outputdata_des = []
        for idx in range(len(names_idx)):
            if names_dim[idx] == '0':
                idp = idp + 1
                outputpara_nam.append(names_nam[idx])
                outputpara_idx.append(names_idx[idx])
                outputpara_txt.append(names_txt[idx])
                outputpara_val.append(names_val[idx])
                outputpara_des.append(names_des[idx])
            else:
                idf = idf + 1
                outputdata_nam.append(names_nam[idx])
                outputdata_idx.append(names_idx[idx])
                outputdata_txt.append(names_txt[idx])
                outputdata_val.append(names_val[idx])
                outputdata_des.append(names_des[idx])
        self.refresh_rpgrid(outputpara_txt, model.res_outputpara)

    def populate_paraspreadsheet_headers(self, spreadsheet_ctrl):
        spreadsheet_ctrl.ClearGrid()
        spreadsheet_ctrl.SetNumberRows(0)
        #
        model = self.view.modeltree.get_model()
        names_txt = []
        names_idx = []
        names_des = []
        names_val = []
        for paramname, param2 in sorted(model.params.iteritems()):
            names_txt.append(param2['name'])
            names_idx.append(param2['index'])
            names_des.append(param2['description'])
            names_val.append(param2['value'])
        param_txt = [' ']*len(names_idx)
        param_des = [' ']*len(names_idx)
        param_val = [' ']*len(names_idx)
        for idx in range(len(names_idx)):
            idx2 = int(names_idx[idx])-1
            param_txt[idx2] = names_txt[idx]
            param_des[idx2] = names_des[idx]
            param_val[idx2] = names_val[idx]
            #
        for row in range(len(param_txt)):
            spreadsheet_ctrl.AppendRows(1)
            spreadsheet_ctrl.SetRowLabelValue(row, param_txt[row])
            spreadsheet_ctrl.SetCellValue(row, 0, param_val[row])
