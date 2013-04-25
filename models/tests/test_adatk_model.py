"""test_adatk_model.py - tests the adatk_model module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import adatk_model
from models.tests import test_podtk_model
import h5py
import numpy as np
import os.path

class TestADAWindowModel(test_podtk_model.TestPODWindowModel):
    """Tests the ADAWindowModel class"""

    def setUp(self):
        self.mock_controller = ""
        self.model = adatk_model.ADAWindowModel(controller=self.mock_controller)
        self.sample_data = np.array(self.random_data())
        self.sample_data_basename = "sample.dat"
        self.sample_data_file = os.path.join(os.path.dirname(__file__),
                                             self.sample_data_basename)
        self.sample_csvdata_basename = "sample.csv"
        self.sample_csvdata_file = os.path.join(os.path.dirname(__file__), self.sample_csvdata_basename)
        np.savetxt(self.sample_csvdata_file, self.sample_data, delimiter=",")
        with h5py.File(self.sample_data_file, 'w') as fidout:
            fidout.create_dataset(self.sample_data_basename, data=self.sample_data)

    def test_load_models(self):
        """Tests the load_models method"""
        ada_models = self.model.load_models()
        for model_name, model_class in ada_models:
            # Basic check to ensure the returned ADA Model name is in the class name
            self.assertTrue(model_name in str(model_class))
            # Ensure the returned class is an ADAModel
            self.assertTrue(issubclass(model_class, adatk_model.ADAModel))

if __name__ == "__main__":
    unittest.main()