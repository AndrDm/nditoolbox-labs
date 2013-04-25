"""file_finder.py - searches for files matching a pattern

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import os
import glob

def exact_match(pattern, path_string):
    """Returns a list of files matching the specified pattern in the specified path.  Essentially a glob.glob
    wrapper."""
    path = os.path.join(path_string, pattern)
    return glob.glob(path)