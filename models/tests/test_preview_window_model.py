"""test_preview_window_model.py - tests the preview_window_model

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

from models import preview_window_model
import h5py
import numpy as np
import os
import random
import unittest

class TestPreviewWindowModel(unittest.TestCase):
    """Tests the PreviewWindowModel"""

    def setUp(self):
        self.mock_ctrl = " "
        self.sample_data = np.array(self.random_data())
        self.sample_data_file = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                              "sample.dat"))
        #np.savetxt(self.sample_data_file, self.sample_data)
        with h5py.File(self.sample_data_file, 'w') as fidout:
            fidout.create_dataset(os.path.basename(self.sample_data_file), data=self.sample_data)

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-100, 100) for i in range(25)]

    def test_init(self):
        """Verify instantiation and initial settings"""
        a_model = preview_window_model.PreviewWindowModel(self.mock_ctrl, self.sample_data_file)
        self.assertEqual(self.sample_data_file, a_model.data_file)
        self.assertIsNone(a_model.data)

    def test_load_data(self):
        """Verify load_data method returns numpy data array"""
        a_model = preview_window_model.PreviewWindowModel(self.mock_ctrl, self.sample_data_file)
        a_model.load_data()
        self.assertListEqual(self.sample_data.tolist(), a_model.data.tolist())

    def tearDown(self):
        if os.path.exists(self.sample_data_file + ".hdf5"):
            os.remove(self.sample_data_file + ".hdf5")

if __name__ == "__main__":
    random.seed()
    unittest.main()