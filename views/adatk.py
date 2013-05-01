"""adatk.py - UI for the Automated Data Analysis (ADA) Toolkit

John C. Aldrin (Computational Tools) and Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'John C. Aldrin and Chris R. Coughlin'

from controllers import adatk_ctrl
from views import wxspreadsheet
from views import wxadamodeltree
from views import wxdirtreectrl
from views import ui_defaults
import matplotlib
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg,\
    FigureCanvasWxAgg as FigureCanvas
import matplotlib.figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import wx
import wx.aui
import wx.grid

widget_margin = 3 # Default margin around widgets
ctrl_pct = 1.0 # Default to 100% resizing factor for controls
lbl_pct = 0.25 # Default to 25% resizing factor for labels
sizer_flags = wx.ALL | wx.EXPAND # Default resizing flags for controls
lblsizer_flags = wx.ALIGN_CENTRE_VERTICAL | wx.ALL # Default resizing flags for labels

class ADAWindow(wx.Frame):
    """Primary interface for ADA Toolkit"""

    def __init__(self, parent):
        _size = wx.Size(1024, 800)
        self.parent = parent
        wx.Frame.__init__(self, id=wx.ID_ANY, name='', parent=self.parent,
                          size=_size, title="ADA Toolkit")
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.version = "03.02.11"
        self.controller = adatk_ctrl.ADAWindowController(self)
        self.ada_config_page = 0 # ADA Configuration page
        self.analysis_dir_page = 1 # Analysis Directory  page
        self.res_summary_page = 2 # Results Summary with Indication (Hole Layout) View page
        self.ind_details_page = 3 # Results Summary with Metrics, Local Plots and Call Descriptions
        #self.ada_designer_page = 4 # ADA Algorithm designer page
        #self.input_sheet_page = 0 # Input data on first notebook page
        #self.output_sheet_page = 1 # Output data on second notebook page
        #self.txtoutput_sheet_page = 2 # Text output on third notebook page
        self.MinSize = wx.Size(600, 800)
        self.init_menu()
        self.init_ui()
        self.SetIcon(parent.GetIcon())

    def init_menu(self):
        """Creates the ADA Toolkit application menu"""
        self.menubar = wx.MenuBar()

        self.file_mnu = wx.Menu() # File menu
        quit_mnui = wx.MenuItem(self.file_mnu, wx.ID_ANY, text="Close Window\tCTRL+W",
                                help="Exits ADAToolkit")
        self.file_mnu.AppendItem(quit_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_quit, quit_mnui)
        self.menubar.Append(self.file_mnu, "&File")

        self.models_mnu = wx.Menu() # Models menu
        #addmodel_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY, text="Add A Model\tCTRL+A",
        #                            help="Adds a ADA model to the available models")
        #self.Bind(wx.EVT_MENU, self.controller.on_add_model, addmodel_mnui)
        #self.models_mnu.AppendItem(addmodel_mnui)

        install_plugin_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY, text="Install Model...",
                                          help="Install a local ADA Model")
        self.Bind(wx.EVT_MENU, self.controller.on_install_model, id=install_plugin_mnui.GetId())
        self.models_mnu.AppendItem(install_plugin_mnui)
        download_plugin_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY, text="Download Model...",
                                           help="Download and install a new ADA Model")
        self.Bind(wx.EVT_MENU, self.controller.on_download_model, id=download_plugin_mnui.GetId())
        self.models_mnu.AppendItem(download_plugin_mnui)

        savemodel_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY,
                                     text="Save Model Configuration",
                                     help="Saves the current model configuration to disk\tCTRL+W")
        self.Bind(wx.EVT_MENU, self.controller.on_save_model, savemodel_mnui)
        self.models_mnu.AppendItem(savemodel_mnui)
        #deletemodel_mnui = wx.MenuItem(self.models_mnu, wx.ID_ANY, text="Remove Current Model",
        #                               help="Removes the currently selected ADA model from the " \
        #                                    "workspace")
        #self.Bind(wx.EVT_MENU, self.controller.on_delete_model, deletemodel_mnui)
        #self.models_mnu.AppendItem(deletemodel_mnui)
        self.menubar.Append(self.models_mnu, "&Models")

        self.ops_mnu = wx.Menu() # Operations menu
        run_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Run\tCTRL+R",
                               help="Runs the current model")
        self.ops_mnu.AppendItem(run_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_runmodel, run_mnui)
        extra_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Test Extract 1\tCTRL+R",
            help="Test Extract Data from ADA Model")
        self.ops_mnu.AppendItem(extra_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_extramodel, extra_mnui)
        testrun_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Test Run 1\tCTRL+R",
            help="Test Run 1 Code")
        self.ops_mnu.AppendItem(testrun_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_testrunmodel, testrun_mnui)
        testrun2_mnui = wx.MenuItem(self.ops_mnu, wx.ID_ANY, text="Test Run 2\tCTRL+R",
            help="Test Run 2 Code")
        self.ops_mnu.AppendItem(testrun2_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_testrunmodel2, testrun2_mnui)
        self.menubar.Append(self.ops_mnu, "&Operation")

        self.help_mnu = wx.Menu() # Basic Help menu
        about_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="About ADA Toolkit",
                                 help="About this program")
        self.help_mnu.AppendItem(about_mnui)
        self.Bind(wx.EVT_MENU, self.controller.on_about, about_mnui)
        help_mnui = wx.MenuItem(self.help_mnu, wx.ID_ANY, text="Usage Basics",
                                help="A rundown of how to use ADA Toolkit to get you started")
        self.Bind(wx.EVT_MENU, self.controller.on_help, help_mnui)
        self.help_mnu.AppendItem(help_mnui)
        self.menubar.Append(self.help_mnu, "&Help")

        self.SetMenuBar(self.menubar)

    def init_ui(self):
        """Generates the user interface"""
        #self.init_ctrls()
        #self.init_plots()
        self.init_spreadsheets()

        # LH of UI - ModelTree pane (upper) and ModelProperty editor pane (lower).
        # Resizable and dockable on left and right of UI.
        #self._mgr.AddPane(self.ctrl_panel, wx.aui.AuiPaneInfo().
        #Name("ctrl_panel").Caption("Models").MinSize(wx.Size(260, 450)).
        #Left().CloseButton(False).MinimizeButton(True).MaximizeButton(True).MinimizeButton(True).
        #Floatable(True).Dockable(False).LeftDockable(True).RightDockable(True))

        #self._mgr.AddPane(self.modelprops_panel, wx.aui.AuiPaneInfo().
        #Name("modelprops_panel").Caption("Model Properties").MinSize(wx.Size(260, 100)).
        #Bottom().Left().CloseButton(False).MinimizeButton(True).MaximizeButton(True)
        #.MinimizeButton(
        #    True).
        #Floatable(True).Dockable(False).LeftDockable(True).RightDockable(True))

        # Center of UI - Input/Output Notebook pane.  Resizable but not dockable.
        self._mgr.AddPane(self.spreadsheet_panel, wx.aui.AuiPaneInfo().
        Name("spreadsheet_panel").Caption("Inputs And Outputs").MinSize(wx.Size(300, 900)).
        Center().CloseButton(False).MinimizeButton(True).MaximizeButton(True).
        Floatable(False).Dockable(False))

        # RH of UI - Plot 1 (above) and Plot 2 (below).  Resizable and dockable on
        # left and right of UI.
        #self._mgr.AddPane(self.plot_panel, wx.aui.AuiPaneInfo().
        #Name("plot_panel").Caption("Plots").MinSize(wx.Size(424, 900)).
        #Right().CloseButton(False).MinimizeButton(True).MaximizeButton(True).
        #Dockable(False).LeftDockable(True).RightDockable(True))

        self._mgr.Update()
        self.status_bar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.status_bar)

    def init_spreadsheets(self):
        """Builds the spreadsheet panels and the text output panel"""
        self.spreadsheet_panel = wx.Panel(self)
        self.spreadsheet_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        #################################################################################
        # Notebook control - first page is input data spreadsheet,
        # second page is output data spreadsheet, third is generic text control for text output.
        self.spreadsheet_nb = wx.Notebook(self.spreadsheet_panel, wx.ID_ANY,
            wx.DefaultPosition, wx.DefaultSize, 0)
        #
        #################################################################################
        # self.ada_config_page = 0 # ADA Configuration page
        self.ctrl_panel0 = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
            wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.output_ctrl_panel0_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.init_ctrls(self.ctrl_panel0)
        #
        self.output_ctrl_panel0_sizer.Add(self.ctrl_panel, 1, wx.TOP | wx.LEFT | wx.GROW)
        self.output_ctrl_panel0_sizer.Add(self.modelprops_panel, 2, wx.TOP | wx.LEFT | wx.GROW)

        self.ctrl_panel0.SetSizer(self.output_ctrl_panel0_sizer)
        self.spreadsheet_nb.AddPage(self.ctrl_panel0, "ADA Configuration", False)
        #
        #################################################################################
        # self.analysis_dir_page = 1 # Run Options page
        self.ctrl_panel1 = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
            wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.output_ctrl_panel1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.left_panel = wx.Panel(self.ctrl_panel1)
        self.left_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        #
        panel1_text1 = wx.StaticText(self.left_panel, wx.ID_ANY, u'Run Type')
        panel1_text1.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        self.left_panel_sizer.Add(panel1_text1, 0,  ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        # - add radiobox (to add sizers)
        #radio_panel = wx.Panel(self.left_panel)
        #radio_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.radioList = [ 'Single File Run (Select File)', 'Validation Study (Set File List)', 'Parametric Study (Set File List and Parameter Levels)', 'Calibration Run',  'Production (Auto-detect) Mode' ]
        self.radioBox1 = wx.RadioBox(self.left_panel,-1, choices = self.radioList, majorDimension=1)
        self.left_panel_sizer.Add(self.radioBox1, lbl_pct, sizer_flags, 0)
        # - add button bar
        btn_panel = wx.Panel(self.left_panel)
        btn_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # - button add dir
        self.adddir_btn = wx.Button(btn_panel, wx.ID_ANY, "Add Folder To List...", wx.DefaultPosition, wx.DefaultSize)
        self.adddir_btn.SetToolTipString("Select a new folder to add to the list")
        self.Bind(wx.EVT_BUTTON, self.controller.on_add_folder, id=self.adddir_btn.GetId())
        btn_panel_sizer.Add(self.adddir_btn, lbl_pct, sizer_flags, widget_margin)
        # - button remove dir
        self.remdir_btn = wx.Button(btn_panel, wx.ID_ANY, "Remove Folder From List...", wx.DefaultPosition, wx.DefaultSize)
        self.remdir_btn.SetToolTipString("Removes selected folder and its subfolders from the list")
        self.Bind(wx.EVT_BUTTON, self.controller.on_remove_folder, id=self.remdir_btn.GetId())
        btn_panel_sizer.Add(self.remdir_btn, lbl_pct, sizer_flags, widget_margin)
        # - add button panel
        btn_panel.SetSizerAndFit(btn_panel_sizer)
        self.left_panel_sizer.Add(btn_panel, lbl_pct, sizer_flags, 0)
        # - add directory tree
        self.dirtree = wxdirtreectrl.DirTreeCtrl(self.left_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize)
        self.dirtree.SetToolTipString("Lists the folders that will be searched for files")
        self.left_panel_sizer.Add(self.dirtree, ctrl_pct, sizer_flags, widget_margin)
        #
        self.listfolders_btn = wx.Button(self.left_panel, wx.ID_ANY, "Generate Folder List", wx.DefaultPosition,
            wx.DefaultSize)
        self.listfolders_btn.SetToolTipString("Lists the folder and its subfolders that will be searched")
        self.Bind(wx.EVT_BUTTON, self.controller.on_folder_list, id=self.listfolders_btn.GetId())
        self.left_panel_sizer.Add(self.listfolders_btn, lbl_pct, lblsizer_flags, widget_margin)
        self.listfolders_lb = wx.ListBox(self.left_panel, wx.ID_ANY, style=wx.LB_EXTENDED)
        self.listfolders_lb.SetToolTipString("Select one or more folders to search, or select none to search all folders listed")
        self.left_panel_sizer.Add(self.listfolders_lb, ctrl_pct, sizer_flags|wx.ALIGN_LEFT, widget_margin)
        #
        self.left_panel.SetSizerAndFit(self.left_panel_sizer)

        #####
        #panel1_sizer12 = wx.BoxSizer(wx.VERTICAL)
        #
        #panel1_text1 = wx.StaticText(self.ctrl_panel1, wx.ID_ANY, u'Directory Tree')
        #panel1_text1.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
        #    70, 90, 92, False, wx.EmptyString))
        #
        #panel1_sizer12.Add(panel1_text1, 0,  ui_defaults.lbl_pct,
        #    ui_defaults.sizer_flags, ui_defaults.widget_margin)
        #panel1_sizer12.Add(self.dir1, 1, wx.TOP | wx.LEFT | wx.GROW)
        #

        #####
        #panel1_sizer11 = wx.BoxSizer(wx.VERTICAL)
        #
        #panel1_text2 = wx.StaticText(self.ctrl_panel1, wx.ID_ANY, u'Auto-Detect Directory')
        #panel1_text2.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
        #    70, 90, 92, False, wx.EmptyString))
        #panel1_text3 = wx.StaticText(self.ctrl_panel1, wx.ID_ANY, u'Batch Directory List')
        #panel1_text3.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
        #    70, 90, 92, False, wx.EmptyString))
        #
        #self.txt_dir1 = wx.TextCtrl(self.ctrl_panel1, wx.ID_ANY,
        #    u'', wx.DefaultPosition, wx.DefaultSize,
        #    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        #self.txt_dirN = wx.TextCtrl(self.ctrl_panel1, wx.ID_ANY,
        #    u'', wx.DefaultPosition, wx.DefaultSize,
        #    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        #

        self.right_panel = wx.Panel(self.ctrl_panel1)
        self.right_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        btn_panel = wx.Panel(self.right_panel)
        btn_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        search_lbl = wx.StaticText(btn_panel, wx.ID_ANY, "Search Selected Folder(s):")
        btn_panel_sizer.Add(search_lbl, lbl_pct, lblsizer_flags, widget_margin)
        file_choices = ['*.hdf5', '*.csv', '*.rf', '*.csc', '*.sdt']
        self.file_cb = wx.ComboBox(btn_panel, wx.ID_ANY, choices=file_choices, style=wx.CB_READONLY)
        self.file_cb.SetToolTipString("Specifies the type of file for which to search")
        self.file_cb.SetSelection(0)
        btn_panel_sizer.Add(self.file_cb, lbl_pct, lblsizer_flags, widget_margin)
        self.searchfiles_btn = wx.Button(btn_panel, wx.ID_ANY, "Search", wx.DefaultPosition, wx.DefaultSize)
        self.searchfiles_btn.SetToolTipString("Searches the selected folder(s) and subfolders for the specified file type")
        self.Bind(wx.EVT_BUTTON, self.controller.on_search_files, id=self.searchfiles_btn.GetId())
        btn_panel_sizer.Add(self.searchfiles_btn, lbl_pct, lblsizer_flags, widget_margin)
        btn_panel.SetSizerAndFit(btn_panel_sizer)
        self.right_panel_sizer.Add(btn_panel, lbl_pct, sizer_flags, 0)

        self.listfiles_lb = wx.ListBox(self.right_panel, wx.ID_ANY, style=wx.TE_MULTILINE)
        self.right_panel_sizer.Add(self.listfiles_lb, ctrl_pct, sizer_flags, widget_margin)

        # - add grid bar
        paragrid_panel = wx.Panel(self.right_panel)
        paragrid_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.input_grid = self.creategrid(paragrid_panel)
        self.input_tb = self.creategrid_toolbar(paragrid_panel)
        #self.init_dir_tree(self.ctrl_panel1) # self.dir_tree

        panel1_text4 = wx.StaticText(self.right_panel, wx.ID_ANY, u'Parametric Study - Value Grid')
        panel1_text4.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        self.right_panel_sizer.Add(panel1_text4, 0,  ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)

        self.input_tb.Realize()
        paragrid_panel_sizer.Add(self.input_tb, 0, wx.EXPAND, border=ui_defaults.widget_margin)
        paragrid_panel_sizer.Add(self.input_grid, 1, wx.TOP | wx.LEFT | wx.GROW)
        #self.output_ctrl_panel1_sizer.Add(panel1_sizer11, 1, wx.ALL | wx.EXPAND)
        #self.output_ctrl_panel1_sizer.Add(self.input_tb, 0, wx.ALL | wx.EXPAND)
        #paragrid_panel_sizer.Add(self.searchfiles_btn, lbl_pct, lblsizer_flags, widget_margin)
        paragrid_panel.SetSizerAndFit(paragrid_panel_sizer)
        self.right_panel_sizer.Add(paragrid_panel, ctrl_pct, sizer_flags, widget_margin)
        self.right_panel.SetSizerAndFit(self.right_panel_sizer)

        #####
        #panel1_sizer11.Add(panel1_text2, 0,  ui_defaults.lbl_pct,
        #    ui_defaults.sizer_flags, ui_defaults.widget_margin)
        #panel1_sizer11.Add(self.txt_dir1, 1, wx.TOP | wx.LEFT | wx.GROW)
        #panel1_sizer11.Add(panel1_text3, 0,  ui_defaults.lbl_pct,
        #    ui_defaults.sizer_flags, ui_defaults.widget_margin)
        #panel1_sizer11.Add(self.txt_dirN, 1, wx.TOP | wx.LEFT | wx.GROW)
        #panel1_sizer11.Add(panel1_text4, 0,  ui_defaults.lbl_pct,
        #    ui_defaults.sizer_flags, ui_defaults.widget_margin)

        # Build  parts
        #self.output_ctrl_panel1_sizer.Add(panel1_sizer12, 1, wx.ALL | wx.EXPAND)
        #self.output_ctrl_panel1_sizer.Add(self.input_tb, 0, wx.ALL | wx.EXPAND)
        #self.output_ctrl_panel1_sizer.Add(panel1_sizer11, 1, wx.ALL | wx.EXPAND)
        #
        self.output_ctrl_panel1_sizer.Add(self.left_panel, 1, wx.ALL | wx.EXPAND)
        self.output_ctrl_panel1_sizer.Add(self.right_panel, 1, wx.ALL | wx.EXPAND)
        #
        self.ctrl_panel1.SetSizer(self.output_ctrl_panel1_sizer)
        self.ctrl_panel1.Layout()
        #
        self.spreadsheet_nb.AddPage(self.ctrl_panel1, "Run Options", False)
        #
        #################################################################################
        # self.res_summary_page = 2 # Results Summary with Indication (Hole Layout) View page
        self.ctrl_panel2 = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
            wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        #splitter = wx.SplitterWindow(self.ctrl_panel2)
        #
        #self.output_ctrl_panel2_sizer = wx.BoxSizer(wx.VERTICAL)
        self.output_ctrl_panel2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel2_sizer21 = wx.BoxSizer(wx.HORIZONTAL)
        panel2_sizer22 = wx.BoxSizer(wx.HORIZONTAL)
        panel2_sizer23 = wx.BoxSizer(wx.VERTICAL) #21 and 22
        #panel2_sizer23 = wx.BoxSizer(wx.HORIZONTAL) #21 and 22
        #
        panel2_text1 = wx.StaticText(self.ctrl_panel2, wx.ID_ANY, u'Indication Summary')
        panel2_text1.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        #
        panel2_text2 = wx.StaticText(self.ctrl_panel2, wx.ID_ANY, u'Status:')
        panel2_text2.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        self.txtoutput_tc = wx.TextCtrl(self.ctrl_panel2, wx.ID_ANY,
            u'', wx.DefaultPosition, wx.DefaultSize,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        #
        self.output_grid = self.creategrid(self.ctrl_panel2)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.controller.on_grid_cellselected,self.output_grid)
        #
        self.output_tb = self.creategrid_toolbar(self.ctrl_panel2)
        self.init_runpropertiesgrid(self.ctrl_panel2) # self.runprops_panel
        self.init_globalplot(self.ctrl_panel2) # self.globalplot_panel
        self.init_plot0(self.ctrl_panel2) # self.plot0_panel
        #
        #####
        self.output_tb.Realize()
        panel2_sizer21.Add(self.output_tb, 0, wx.EXPAND, border=ui_defaults.widget_margin)
        panel2_sizer21.Add(self.output_grid, 1, wx.TOP | wx.LEFT | wx.GROW)
        #
        panel2_sizer22.Add(self.runprops_panel, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        panel2_sizer22.Add(wx.StaticLine(self.ctrl_panel2, -1))
        panel2_sizer22.Add(self.globalplot_panel, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        #
        panel2_sizer23.Add(panel2_text1, 0,  ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        panel2_sizer23.Add(panel2_sizer21, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        panel2_sizer23.Add(panel2_sizer22, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        panel2_sizer23.Add(panel2_text2, 0, ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        panel2_sizer23.Add(self.txtoutput_tc, 0, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        #
        self.output_ctrl_panel2_sizer.Add(panel2_sizer23, 1, wx.ALL | wx.EXPAND)
        self.output_ctrl_panel2_sizer.Add(self.plot0_panel, 1, wx.ALL | wx.EXPAND)
        #splitter.SplitVertically(panel2_sizer23, self.plot0_panel)
        #self.output_ctrl_panel2_sizer.Add(splitter, 1, wx.EXPAND)
        #
        self.ctrl_panel2.SetSizer(self.output_ctrl_panel2_sizer)
        self.ctrl_panel2.Layout()
        #
        self.spreadsheet_nb.AddPage(self.ctrl_panel2, "Results Summary", False)
        #
        #################################################################################
        # self.res_details_page = 3 # Indication Details with Visual Results/Call Description Views
        self.ctrl_panel3 = wx.Panel(self.spreadsheet_nb, wx.ID_ANY,
            wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        #splitter = wx.SplitterWindow(self.ctrl_panel2)
        #
        self.output_ctrl_panel3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel3_sizer31 = wx.BoxSizer(wx.HORIZONTAL)
        panel3_sizer32 = wx.BoxSizer(wx.HORIZONTAL)
        panel3_sizer33 = wx.BoxSizer(wx.VERTICAL) #21 and 22
        panel3_sizer34 = wx.BoxSizer(wx.VERTICAL)
        #
        panel3_text1 = wx.StaticText(self.ctrl_panel3, wx.ID_ANY, u'Indication Metrics')
        panel3_text1.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        #
        self.output_grid2 = self.creategrid(self.ctrl_panel3)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.controller.on_grid2_cellselected,self.output_grid2)
        self.output_tb2 = self.creategrid_toolbar(self.ctrl_panel3)
        #
        panel3_text2 = wx.StaticText(self.ctrl_panel3, wx.ID_ANY, u'Call Description')
        panel3_text2.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        self.txtind = wx.TextCtrl(self.ctrl_panel3, wx.ID_ANY,
            u'', wx.DefaultPosition, wx.DefaultSize,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        #
        self.init_localplot2(self.ctrl_panel3) # self.localplot2_panel
        self.init_plots(self.ctrl_panel3) # self.plot_panel
        #
        #####
        self.output_tb2.Realize()
        panel3_sizer31.Add(self.output_tb2, 0, wx.EXPAND, border=ui_defaults.widget_margin)
        panel3_sizer31.Add(self.output_grid2, 1, wx.TOP | wx.LEFT | wx.GROW)
        #
        panel3_sizer34.Add(panel3_text2, 0,  ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        panel3_sizer34.Add(self.txtind , 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        #
        panel3_sizer32.Add(panel3_sizer34, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        panel3_sizer32.Add(wx.StaticLine(self.ctrl_panel3, -1))
        panel3_sizer32.Add(self.localplot2_panel, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        #
        panel3_sizer33.Add(panel3_text1, 0,  ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        panel3_sizer33.Add(panel3_sizer31, 1, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        panel3_sizer33.Add(panel3_sizer32, 0.5, wx.ALL | wx.EXPAND, border=ui_defaults.widget_margin)
        #
        self.output_ctrl_panel3_sizer.Add(panel3_sizer33, 1, wx.ALL | wx.EXPAND)
        self.output_ctrl_panel3_sizer.Add(self.plot_panel, 1, wx.ALL | wx.EXPAND)
        #
        self.ctrl_panel3.SetSizer(self.output_ctrl_panel3_sizer)
        self.ctrl_panel3.Layout()
        #
        self.spreadsheet_nb.AddPage(self.ctrl_panel3, "Indication Details", False)
        #################################################################################
        self.spreadsheet_panel_sizer.Add(self.spreadsheet_nb, 1,
            wx.TOP | wx.LEFT | wx.GROW, ui_defaults.widget_margin)
        self.spreadsheet_panel.SetSizer(self.spreadsheet_panel_sizer)

    def init_ctrls(self, parent):
        """Builds the ModelTree and ModelProperty editor panes (LH of UI)."""
        self.ctrl_panel = wx.Panel(parent)
        self.ctrl_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.init_modeltree()
        self.init_modelpropertiesgrid(parent)
        self.ctrl_panel.SetSizer(self.ctrl_panel_sizer)

    def init_modeltree(self):
        """Builds the ModelTree"""
        self.modeltree = wxadamodeltree.ModelTree(self.ctrl_panel, wx.ID_ANY,
            style=wx.WANTS_CHARS | wx.TR_DEFAULT_STYLE)
        self.modeltree.Expand(self.modeltree.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.controller.on_selection_change, self.modeltree)
        self.Bind(wx.EVT_TREE_SET_INFO, self.controller.on_modeltree_change, self.modeltree)
        self.modeltree.Bind(wx.EVT_RIGHT_DOWN, self.controller.on_right_click_modeltree)
        self.ctrl_panel_sizer.Add(self.modeltree, ui_defaults.ctrl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.controller.get_models()

    def init_modelpropertiesgrid(self,parent):
        """Builds the ModelProperty editor"""
        self.modelprops_panel = wx.Panel(parent)
        self.modelprops_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.mp_lbl = wx.StaticText(self.modelprops_panel, wx.ID_ANY,
                                    u"No Property Selected", wx.DefaultPosition, wx.DefaultSize, 0)
        self.modelprops_panel_sizer.Add(self.mp_lbl, ui_defaults.lbl_pct,
                                        ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.mp_grid = wxspreadsheet.Spreadsheet(self.modelprops_panel)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.controller.on_property_change)
        self.mp_grid.SetNumberRows(1)
        self.mp_grid.SetNumberCols(2)
        self.mp_grid.SetRowLabelSize(1)
        ro_attrib = wx.grid.GridCellAttr()
        ro_attrib.SetReadOnly()
        self.mp_grid.SetColAttr(0, ro_attrib)
        self.mp_grid.SetColSize(0, 125)
        self.mp_grid.SetColSize(1, 500)
        self.mp_grid.SetColMinimalAcceptableWidth(100)
        self.mp_grid.SetColLabelValue(0, "Property")
        self.mp_grid.SetColLabelValue(1, "Value")
        self.mp_grid.EnableEditing(True)
        self.modelprops_panel_sizer.Add(self.mp_grid, ui_defaults.ctrl_pct,
                                        ui_defaults.sizer_flags | wx.GROW,
                                        ui_defaults.widget_margin)
        self.modelprops_panel.SetSizer(self.modelprops_panel_sizer)

    def init_runpropertiesgrid(self, parent):
        """Builds the Run Property view"""
        self.runprops_panel = wx.Panel(parent)
        self.runprops_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.rp_lbl = wx.StaticText(self.runprops_panel, wx.ID_ANY,
            u"Run Conditions", wx.DefaultPosition, wx.DefaultSize, 0)
        self.rp_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        self.runprops_panel_sizer.Add(self.rp_lbl, ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)

        self.rp_grid = wxspreadsheet.Spreadsheet(self.runprops_panel)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.controller.on_property_change)
        self.rp_grid.SetNumberRows(1)
        self.rp_grid.SetNumberCols(2)
        self.rp_grid.SetRowLabelSize(1)
        ro_attrib = wx.grid.GridCellAttr()
        ro_attrib.SetReadOnly()
        self.rp_grid.SetColAttr(0, ro_attrib)
        self.rp_grid.SetColSize(0, 100)
        self.rp_grid.SetColSize(1, 150)
        self.rp_grid.SetColMinimalAcceptableWidth(100)
        self.rp_grid.SetColLabelValue(0, "Property")
        self.rp_grid.SetColLabelValue(1, "Value")
        self.rp_grid.EnableEditing(True)
        self.runprops_panel_sizer.Add(self.rp_grid, ui_defaults.ctrl_pct,
            ui_defaults.sizer_flags | wx.GROW,
            ui_defaults.widget_margin)
        self.runprops_panel.SetSizer(self.runprops_panel_sizer)

    def init_globalplot(self, parent):
        """Builds the Run Property view"""
        self.globalplot_panel = wx.Panel(parent)
        self.globalplot_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.gp_lbl = wx.StaticText(self.globalplot_panel, wx.ID_ANY,
            u"Global Plot", wx.DefaultPosition, wx.DefaultSize, 0)
        self.gp_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        self.globalplot_panel_sizer.Add(self.gp_lbl, ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)

        cscan_list = ['AMP1', 'TOF1', 'TOF2']
        self.gp_listbox = wx.ListBox(self.globalplot_panel, 26, wx.DefaultPosition, (170, 130), cscan_list, wx.LB_SINGLE)
        self.gp_listbox.SetSelection(0)
        self.gp_listbox.Bind(wx.EVT_LISTBOX, self.controller.on_gplistbox_change, id=26)

        self.globalplot_panel_sizer.Add(self.gp_listbox, ui_defaults.ctrl_pct,
            ui_defaults.sizer_flags | wx.GROW,
            ui_defaults.widget_margin)
        self.globalplot_panel.SetSizer(self.globalplot_panel_sizer)


    def init_localplot2(self, parent):
        """Builds the Run Property view"""
        self.localplot2_panel = wx.Panel(parent)
        self.localplot2_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.lp_lbl = wx.StaticText(self.localplot2_panel, wx.ID_ANY,
            u"Local Plots", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lp_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))

        self.lp_lbl1 = wx.StaticText(self.localplot2_panel, wx.ID_ANY,
            u"Plot 1:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lp_lbl2 = wx.StaticText(self.localplot2_panel, wx.ID_ANY,
            u"Plot 2:", wx.DefaultPosition, wx.DefaultSize, 0)
        plot_list = ['C-Scan:AMP1', 'C-Scan:TOF1', 'C-Scan:TOF2', 'A-Scan', ]

        self.lp_listbox1 = wx.ListBox(self.localplot2_panel, 4, wx.DefaultPosition, (170, 60), plot_list, wx.LB_SINGLE)
        self.lp_listbox1.SetSelection(0)
        self.lp_listbox1.Bind(wx.EVT_LISTBOX, self.controller.on_lplistbox1_change)

        self.lp_listbox2 = wx.ListBox(self.localplot2_panel, 4, wx.DefaultPosition, (170, 60), plot_list, wx.LB_SINGLE)
        self.lp_listbox2.SetSelection(1)
        self.lp_listbox2.Bind(wx.EVT_LISTBOX, self.controller.on_lplistbox2_change)

        self.localplot2_panel_sizer.Add(self.lp_lbl, ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.localplot2_panel_sizer.Add(self.lp_lbl1, ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.localplot2_panel_sizer.Add(self.lp_listbox1, ui_defaults.ctrl_pct,
            ui_defaults.sizer_flags | wx.GROW, ui_defaults.widget_margin)
        self.localplot2_panel_sizer.Add(self.lp_lbl2, ui_defaults.lbl_pct,
            ui_defaults.sizer_flags, ui_defaults.widget_margin)
        self.localplot2_panel_sizer.Add(self.lp_listbox2, ui_defaults.ctrl_pct,
            ui_defaults.sizer_flags | wx.GROW, ui_defaults.widget_margin)
        self.localplot2_panel.SetSizer(self.localplot2_panel_sizer)

    def init_plot0(self, parent):
        """Builds the single plot panel"""
        self.plot0_panel = wx.Panel(parent)
        self.plot0_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.figure0 = matplotlib.figure.Figure((5, 4), 75)
        self.canvas0 = FigureCanvas(self.plot0_panel, -1, self.figure0)
        self.toolbar0 = NavigationToolbar2WxAgg(self.canvas0)

        self.axes0 = self.figure0.add_subplot(111, navigate=True)
        self.axes0.grid(True)

        cscan_panel = wx.Panel(self.plot0_panel)
        cscan_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        plot0_lbl = wx.StaticText(cscan_panel, wx.ID_ANY, u"C-Scan Viewer",
            wx.DefaultPosition, wx.DefaultSize, 0)
        plot0_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
            70, 90, 92, False, wx.EmptyString))
        cscan_panel_sizer.Add(plot0_lbl, lbl_pct, lblsizer_flags, widget_margin)

        self.plot0_txt0 = wx.TextCtrl(cscan_panel, wx.ID_ANY, u"0",
            wx.DefaultPosition, wx.DefaultSize, 0)
        cscan_panel_sizer.Add(self.plot0_txt0, lbl_pct, lblsizer_flags, widget_margin)

        self.plot0_txt1 = wx.TextCtrl(cscan_panel, wx.ID_ANY, u"1",
            wx.DefaultPosition, wx.DefaultSize, 0)
        cscan_panel_sizer.Add(self.plot0_txt1, lbl_pct, lblsizer_flags, widget_margin)

        self.replot_btn = wx.Button(cscan_panel, wx.ID_ANY, "Replot", wx.DefaultPosition, wx.DefaultSize)
        self.Bind(wx.EVT_BUTTON, self.controller.on_gpreplot_change, id=self.replot_btn.GetId())
        cscan_panel_sizer.Add(self.replot_btn, lbl_pct, lblsizer_flags, widget_margin)

        self.plot0_lblz = wx.StaticText(cscan_panel, wx.ID_ANY, u"         ",
            wx.DefaultPosition, wx.DefaultSize, 0)
        cscan_panel_sizer.Add(self.plot0_lblz, lbl_pct, lblsizer_flags, widget_margin)

        #plot0_lbly = wx.StaticText(cscan_panel, wx.ID_ANY, u"y= 0.0000",
        #    wx.DefaultPosition, wx.DefaultSize, 0)
        #cscan_panel_sizer.Add(plot0_lbly, lbl_pct, lblsizer_flags, widget_margin)

        cscan_panel.SetSizerAndFit(cscan_panel_sizer)

        self.plot0_panel_sizer.Add(cscan_panel, 0, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        self.plot0_panel_sizer.Add(self.canvas0, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        self.plot0_panel_sizer.Add(self.toolbar0, 0, ui_defaults.sizer_flags,
            ui_defaults.widget_margin)
        self.toolbar0.Realize()
        self.plot0_panel.SetSizer(self.plot0_panel_sizer)

    def init_plots(self, parent):
        """Builds the two plot windows"""
        self.plot_panel = wx.Panel(parent)
        self.plot_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.figure1 = matplotlib.figure.Figure((5, 4), 75)
        self.figure2 = matplotlib.figure.Figure((5, 4), 75)
        self.canvas1 = FigureCanvas(self.plot_panel, -1, self.figure1)
        self.canvas2 = FigureCanvas(self.plot_panel, -1, self.figure2)
        self.toolbar1 = NavigationToolbar2WxAgg(self.canvas1)

        self.toolbar2 = NavigationToolbar2WxAgg(self.canvas2)

        self.axes1 = self.figure1.add_subplot(111, navigate=True)
        self.axes1.grid(True)
        self.axes2 = self.figure2.add_subplot(111, navigate=True)
        self.axes2.grid(True)
        plot1_lbl = wx.StaticText(self.plot_panel, wx.ID_ANY, u"Plot 1",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        plot1_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
                                  70, 90, 92, False, wx.EmptyString))
        plot2_lbl = wx.StaticText(self.plot_panel, wx.ID_ANY, u"Plot 2",
                                  wx.DefaultPosition, wx.DefaultSize, 0)
        plot2_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(),
                                  70, 90, 92, False, wx.EmptyString))
        self.plot_panel_sizer.Add(plot1_lbl, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.canvas1, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.toolbar1, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.toolbar1.Realize()
        self.plot_panel_sizer.Add(plot2_lbl, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.canvas2, ui_defaults.ctrl_pct, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.plot_panel_sizer.Add(self.toolbar2, 0, ui_defaults.sizer_flags,
                                  ui_defaults.widget_margin)
        self.toolbar2.Realize()
        self.plot_panel.SetSizer(self.plot_panel_sizer)

    def init_dir_tree(self, parent):

        self.dir_tree = wx.Panel(parent)
        dir_tree_sizer = wx.BoxSizer(wx.VERTICAL)
        #txt1 = wx.StaticText(self, -1, "style=0")
        #dir_tree_sizer.Add((35, 35)) # some space above
        #dir_tree_sizer.Add(txt1)
        self.dir1 = wx.GenericDirCtrl(parent, -1, size=(200,225), style=wx.DIRCTRL_DIR_ONLY)
        dir_tree_sizer.Add(self.dir1, 0, wx.EXPAND)
        self.SetSizer(dir_tree_sizer)
        self.SetAutoLayout(True)
        # events
        #self.dir_tree1 = self.dirBrowser.GetTreeCtrl()
        self.dir1.Bind(wx.EVT_TREE_SEL_CHANGED, self.controller.on_property_change)
        #t = dir1.GetTreeCtrl()
        #t.Bind(wx.EVT_TREE_SEL_CHANGED, self.test)

    def creategrid(self, parent, numcols=None, numrows=None):
        """Builds and returns a new Spreadsheet with the specified
        number of columns and rows."""
        newgrid = wxspreadsheet.Spreadsheet(parent)
        if numcols is not None:
            newgrid.SetNumberCols(numcols)
        if numrows is not None:
            newgrid.SetNumberRows(numrows)
        newgrid.ForceRefresh()
        newgrid.EnableEditing(True)
        newgrid.EnableGridLines(True)
        newgrid.EnableDragGridSize(False)
        newgrid.EnableDragColMove(True)
        newgrid.EnableDragColSize(True)
        newgrid.EnableDragRowSize(True)
        newgrid.EnableDragGridSize(True)
        newgrid.SetMargins(0, 0)
        newgrid.SetColLabelSize(30)
        newgrid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        return newgrid

    def creategrid_toolbar(self, parent):
        """Creates a toolbar for a Spreadsheet control - includes open
        and save functions."""
        toolbar = wx.ToolBar(parent,
                             style=wx.TB_VERTICAL | wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        tsize = (16, 16)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tsize)

        toolbar.SetToolBitmapSize(tsize)
        toolbar.AddLabelTool(20, "Open", open_bmp, shortHelp="Open ")
        toolbar.AddSimpleTool(30, save_bmp, "Save", "Long help for 'Save'")
        self.Bind(wx.EVT_TOOL, self.controller.on_sheet_tool_click, id=20)
        self.Bind(wx.EVT_TOOL, self.controller.on_sheet_tool_click, id=30)
        return toolbar

    def tree_popup(self, click_position):
        """Generates a contextual (popup) menu for the ModelTree"""
        self.PopupMenu(wxadamodeltree.ModelTreeContextMenu(self), click_position)

    def close(self):
        """Correctly handles UI shutdown"""
        self._mgr.UnInit()
        self.Destroy()