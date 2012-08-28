"""adatk_model.py - model for the ADA Toolkit

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin and John C. Aldrin'

from controllers import pathfinder
from models import abstractplugin
from models import mainmodel
from models import podtk_model
from configobj import ConfigObj
import os.path


class ADAWindowModel(podtk_model.PODWindowModel):
    """Model for the ADAWindow UI"""

    def load_models(self):
        """Searches the ADA Models folder and imports all valid models,
        returning a list of the models successfully imported as tuples:
        first element is the model name (e.g. AHat_v_A), second element is
        the class of the model."""
        return mainmodel.load_dynamic_modules(pathfinder.adamodels_path(), ADAModel)

class ADAModel(abstractplugin.ComputationalToolsPlugin):
    """Base analysis class for the ADA Toolkit"""
    description = ""
    inputdata = {}
    outputdata = {}
    indcalls = {}
    indmetrics = {}
    inddata = {}
    params = {}
    settings = {}

    def __init__(self, name, description=None, inputdata=None, outputdata=None, indcalls=None,
                 indmetrics=None, inddata=None, params=None, settings=None):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if inputdata is not None:
            self.inputdata = inputdata
        if outputdata is not None:
            self.outputdata = outputdata
        if indcalls is not None:
            self.indcalls = indcalls
        if indmetrics is not None:
            self.indmetrics = indmetrics
        if inddata is not None:
            self.inddata = inddata
        if params is not None:
            self.params = params
        if settings is not None:
            self.settings = settings
        self._data = None
        self.res_outputdata = None
        self.config = os.path.join(pathfinder.adamodels_path(), self.__module__ + '.cfg')
        self.results = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        self._data = new_data

    def run(self):
        """Executes the plugin (no-op in base class)"""
        pass

    def plot0(self, axes_hdl, fig_hdl):
        """Generates the primary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def plot1(self, axes_hdl, fig_hdl):
        """Generates the primary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def plot2(self, axes_hdl, fig_hdl):
        """Generates the secondary plot on the specified matplotlib Axes instance
        (no-op in base class)."""
        pass

    def configure(self):
        """Reads the ADAModel's configuration file and configures
        the model accordingly."""
        if self.config is not None:
            if os.path.exists(self.config):
                config = ConfigObj(self.config)
                config_keys = config.keys()
                if 'Input Data' in config_keys:
                    self.inputdata = config['Input Data']
                if 'Output Data' in config_keys:
                    self.outputdata = config['Output Data']
                if 'Indication Calls' in config_keys:
                    self.indcalls = config['Indication Calls']
                if 'Indication Metrics' in config_keys:
                    self.indmetrics = config['Indication Metrics']
                if 'Indication Data' in config_keys:
                    self.inddata = config['Indication Data']
                if 'Parameters' in config_keys:
                    self.params = config['Parameters']
                if 'Settings' in config_keys:
                    self.settings = config['Settings']

    def save_configuration(self):
        """Saves the current configuration to disk"""
        if self.config is not None:
            config = ConfigObj(self.config)
            config['Input Data'] = self.inputdata
            config['Output Data'] = self.outputdata
            config['Indication Calls'] = self.indcalls
            config['Indication Metrics'] = self.indmetrics
            config['Indication Data'] = self.inddata
            config['Parameters'] = self.params
            config['Settings'] = self.settings
            config.write()
