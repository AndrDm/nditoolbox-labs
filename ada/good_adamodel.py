# This import you need
from models.adatk_model import ADAModel
# Everything else depends on what your model requires
import numpy as np
import time

# All ADA Models must be a subclass of ADAModel
class CompositeADABasic1(ADAModel):

    # All ADA Models must define the following information fields.
    name = "composites ADA basic 1"
    description = "Composites ADA  - Basic Model 1"
    authors = "Computational Tools and TRI/Austin, Inc."
    version = "1.0"
    url = "www.nditoolbox.com"
    copyright = ""
    
    def __init__(self):
        ADAModel.__init__(self, self.name, self.description, self.inputdata, self.outputdata, self.indcalls,
            self.indmetrics, self.inddata, self.params, self.settings)

    def run(self):
        """Executes the ADA Model"""
        
        # Example busy work
        print("Input Data Configuration:")
        for key, value in self.inputdata.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\nOutput Data Configuration:")
        for key, value in self.outputdata.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\nIndication Calls Configuration:")
        for key, value in self.indcalls.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\nIndication Metrics Configuration:")
        for key, value in self.indmetrics.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\nIndication Data Configuration:")
        for key, value in self.inddata.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\nParameters Configuration:")
        for key, value in self.params.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\nSettings Configuration:")
        for key, value in self.settings.iteritems():
            print("\t{0}={1}".format(key, value))
        print("\n")
        for i in range(5):
            msg = "*"*i
            print(msg)
            time.sleep(1)
            
        # To display tabular data after execution, set self._data to your output data
        # ADA Toolkit will load the NumPy array and display it automatically.
        # You can safely ignore this if you don't need to display data.
        self._data = np.array([np.arange(0., 2.2, 0.2), np.arange(0., 4.4, 0.4)])
        #
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
        self.res_outputdata.append(1*np.random.rand(Nx,Ny)+0.01*yy)
        self.res_outputdata.append(1*np.random.rand(Nx,Ny)+0.01*xx+0.01*yy)
        self.res_outputdata.append(10*np.random.rand(Nx,Ny))
        self.res_outputdata.append(ta)
        #
        #self.res_outputdata = []
        #self.res_outputdata[1].dim = 2
        #self.res_outputdata[1].array = 10*np.random.rand(Nx,Ny)
        #
        # To display a text summary after execution, set self.results
        # ADA Toolkit will display this text in the text output field automatically.
        # You can safely ignore this if you don't need to display a text summary.
        self.results = "Sample ADA Model completed successfully."

    def plot0(self, axes_hdl, fig_hdl):
        """Generates global C-scan plot view."""
        # Example of plotting - if you have no primary plot, no need to define a plot1 method.
        X = 10*np.random.rand(300,400)
        #
        axes_hdl.clear()
        fig_hdl.clear() #in case there are extra axes like colorbars
        axes_hdl = fig_hdl.add_subplot(111, navigate=True)
        #
        cax = axes_hdl.imshow(X)
        fig_hdl.colorbar(cax)
        #
        axes_hdl.set_title("C-scan")
        axes_hdl.set_xlabel("X Axis")
        axes_hdl.set_ylabel("Y Axis")

    def plot1(self, axes_hdl, fig_hd):
        """Generates the primary plot on the specified matplotlib Axes instance."""
        
        # Example of plotting - if you have no primary plot, no need to define a plot1 method.
        axes_hdl.plot([1,2,3,4], [1,4,9,16], 'ro')
        axes_hdl.axis([0, 6, 0, 20])
        axes_hdl.set_title("Example Plot 1")
        axes_hdl.set_xlabel("X Axis")
        axes_hdl.set_ylabel("Y Axis")

    def plot2(self, axes_hdl, fig_hd):
        """Generates the secondary plot on the specified matplotlib Axes instance."""
        
        # Example of plotting - if you have no secondary plot, no need to define a plot2 method.
        t = np.arange(0., 5., 0.2)
        axes_hdl.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')
        axes_hdl.set_title("Example Plot 2")
        axes_hdl.set_xlabel("X Axis")
        axes_hdl.set_ylabel("Y Axis")
        axes_hdl.legend(("Linear", "Square", "Cubic"), 'upper right', title="Functions", shadow=True, fancybox=True)