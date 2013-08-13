
"""DSF_podtk_model.py - model for the POD Toolkit

Chris R. Coughlin, David S. Forsyth (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
from models import abstractplugin
from models import mainmodel
from configobj import ConfigObj
import imp
import inspect
import os.path
import sys
import xlrd
import datetime
import numpy as np

class DSF_PODData(object):
    """ This is the Model for a MVC architecture, or in other words the data"""
    #input_sizes is an ndarray we define later when we know size
    #input_results is an ndarray we define later when we know size
    title = ''
    date = datetime.datetime(1,1,1)
    analyst = ''
    description = ''
    POD_type = 'hit/miss'
    title_sizes = 'black hole size (parsecs)'
    title_results = 'inspection result (cubits)'
    num_opps = 0
    num_cracks = 0
    num_false = 0
    col_results = 4
    col_sizes = 2
    pod_models = []
    active_model_idx = 0
    is_data_loaded = False

    def __init__(self, controller):
        self.controller = controller
        is_data_loaded = False
        file_name = ""

    def load_models(self):
        """Searches the POD Models folder and imports all valid models,
        returning a list of the models successfully imported as tuples:
        first element is the model name (e.g. AHat_v_A), second element is
        the class of the model."""
        models_folder = pathfinder.podmodels_path()
        if not models_folder in sys.path:
            sys.path.append(models_folder)
        for root, dir, files in os.walk(pathfinder.podmodels_path()):
            for model_file in files:
                model_name, model_extension = os.path.splitext(model_file)
                module_hdl = None
                if model_extension == os.extsep + "py":
                    try:
                        module_hdl, path_name, description = imp.find_module(model_name)
                        podmodel_module = imp.load_module(model_name, module_hdl, path_name,
                            description)
                        podmodel_classes = inspect.getmembers(podmodel_module, inspect.isclass)
                        for podmodel_class in podmodel_classes:
                            if issubclass(podmodel_class[1], PODModel):
                                if podmodel_class[1].__module__ == model_name:
                                    self.pod_models.append(podmodel_class)
                    finally:
                        if module_hdl is not None:
                            module_hdl.close()
        return self.pod_models

    def get_models(self):
        """
        Returns the list of the PODModel's that are available, loads them if not already loaded
        """
        if len(self.pod_models) == 0:
            self.load_models()

        return self.pod_models

    def import_data(self, file_name):
        """
        Get the raw data from an excel file. Not just any excel file of course, but one set up for this purpose.
        """
        excel_file = xlrd.open_workbook(file_name)
        if excel_file is None:
            return False

        """ TODO error, range checking"""
        summary_sheet = excel_file.sheet_by_name('Summary')
        self.title = summary_sheet.cell(6,3).value
        self.date = xlrd.xldate_as_tuple(summary_sheet.cell(8,3).value,excel_file.datemode)
        self.analyst = summary_sheet.cell(10,3)
        self.description = summary_sheet.cell(12,3)
        self.POD_Type = summary_sheet.cell(19,3)
        self.num_opps = summary_sheet.cell(20,3)
        self.num_cracks = summary_sheet.cell(21,3)
        self.num_false = summary_sheet.cell(22,3)
        self.is_data_loaded = True
        self.file_name = file_name

        data_sheet = excel_file.sheet_by_name('Sheet1')
        data_rows = data_sheet.nrows
        self.input_sizes = np.ndarray(data_rows, dtype = float)
        self.input_results = np.ndarray(data_rows, dtype = float)
        self.title_sizes = data_sheet.cell(0,self.col_sizes-1)
        self.title_results = data_sheet.cell(0,self.col_results-1)

        """ wacky indexing... xlrd uses zero indexing
        so that means input_sizes[0] is at row 2 in Excel address which is addressed as row 1 by xlrd
        and there are data_rows - 1 data points cause first row is title"""
        for i in range(0,data_rows-1,1):
            self.input_sizes[i] = data_sheet.cell(i+1, self.col_sizes-1).value
            self.input_results[i] = data_sheet.cell(i+1, self.col_results-1).value

        # Now we have data, might as well get the models
        self.load_models()
        return True

    def export_data(self, file_name, data):
        """Saves NumPy array data to the specified file name"""
        export_params = {'delimiter': ','}
        mainmodel.save_data(file_name, data, **export_params)

    def get_file_name(self):
        """
        Serve up the file name to anyone who cares.
        """
        return self.file_name

    def plot_input_data(self, axes_hdl):
        """
        Have input data? Plot it.
        """
        if self.is_data_loaded is False:
            return
        axes_hdl.cla()
        axes_hdl.plot(self.input_sizes,self.input_results,'b.')
        axes_hdl.set_title(self.title)
        axes_hdl.set_xlabel(self.title_sizes)
        axes_hdl.set_ylabel(self.title_results)
        return

    def plot_likelihood(self, axes_hdl):
        """
        Calls the active model to plot likelihood
        """
        if self.is_data_loaded is False:
            return

        self.pod_models[active_model_idx].plot_likelihood(axes_hdl)

        axes_hdl.cla()
        axes_hdl.plot(self.input_sizes,self.input_results,'b.')
        axes_hdl.set_title(self.title)
        axes_hdl.set_xlabel(self.title_sizes)
        axes_hdl.set_ylabel(self.title_results)
        return

    def run(self):
        """
        Runs the active model
        """
        if self.is_data_loaded is False:
            return
        a_model_class = self.pod_models[1]
        a_model = a_model_class[1]()
        a_model.run(self.input_sizes, self.input_results, self.num_cracks,
                                                self.num_false, self.num_opps)
        return



class DSF_PODModel(abstractplugin.TRIPlugin):
    """Base analysis class for the DSF POD Toolkit"""
    description = "TRI/Austin toolkit for probability of detection"
    name = "TRI/Austin POD"
    inputdata = {}
    params = {}
    settings = {}

    def __init__(self, name, description=None, inputdata=None, params=None,
                 settings=None):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if inputdata is not None:
            self.inputdata = inputdata
        if params is not None:
            self.params = params
        if settings is not None:
            self.settings = settings
        self._data = None
        self.config = os.path.join(pathfinder.podmodels_path(), self.__module__ + '.cfg')
        self.results = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data

    def run(self, input_sizes, input_results, num_cracks, num_false, num_opps):
        """Executes the plugin (no-op in base class)"""
        pass

    def plot_raw_data(self, axes_hdl):
        """Generates the primary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def plot_POD_results(self, axes_hdl):
        """Generates the secondary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def plot_likelihood(self, axes_hdl):
        """Generates the likelihood data plot on the specified matplotlib Axes instance
         (no-op in base class)."""
        pass

    def configure(self):
        """Reads the PODModel's configuration file and configures
        the model accordingly."""
        if self.config is not None:
            if os.path.exists(self.config):
                config = ConfigObj(self.config)
                config_keys = config.keys()
                if 'Input Data' in config_keys:
                    self.inputdata = config['Input Data']
                if 'Parameters' in config_keys:
                    self.params = config['Parameters']
                if 'Settings' in config_keys:
                    self.settings = config['Settings']

    def save_configuration(self):
        """Saves the current configuration to disk"""
        if self.config is not None:
            config = ConfigObj(self.config)
            config['Input Data'] = self.inputdata
            config['Parameters'] = self.params
            config['Settings'] = self.settings
            config.write()