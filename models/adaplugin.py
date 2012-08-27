"""adaplugin.py - defines the automated defect analysis (ADA) plugin for NDIToolbox

John C. Aldrin (Computational Tools)
"""

__author__ = 'John C. Aldrin'

from abstractplugin import ComputationalToolsPlugin

class ADAPlugin(ComputationalToolsPlugin):
    """Abstract base class definition for NDIToolbox plugins.  Plugins must
    be a subclass of AbstractPlugin and must define the following members.

    data - getter and setter - NumPy array
    description - getter - str
    authors - getter - str
    copyright - getter - str
    name - getter - str
    version - getter - str
    url - getter - str
    run() method
    """

    name = "Computational Tools Plugin"
    description = "Basic template for creating NDIToolbox plugins for Computational Tools personnel."
    authors = "John C. Aldrin (Computational Tools, Inc.)"
    version = "1.0"
    url = "www.computationaltools.com"
    copyright = "Copyright (C) 2012 Computational Tools.  All rights reserved."

    def __init__(self, name=None, description=None, authors=None, version=None,
                 url=None, copyright=None):
        super(ComputationalToolsPlugin, self).__init__(name, description, authors, version,
                                                       url, copyright)
