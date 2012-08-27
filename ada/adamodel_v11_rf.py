# This import you need
from models.adatk_model import ADAModel
# Everything else depends on what your model requires
import numpy as np
import time

import tkFileDialog
import array
import Image
import cv2
from cv2 import cv

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

        ############################################################################
        model = self
        ############################################################################
        self.load_rf()
        #
        Nx, Ny, Nt = self.inter_data.shape
        #
        datatmp_1 = self.inter_data.max(2) - self.inter_data.min(2)
        data_1 = datatmp_1.astype('f')
        #
        datatmp_2 = self.inter_data.argmax(2) + self.inter_data.argmin(2)
        data_2 = 0.5*datatmp_2.astype('f')
        #
        inter_dataA = self.inter_data[:,:,29:135]
        datatmp_3 = inter_dataA.max(2) - inter_dataA.min(2)
        data_3 = datatmp_3.astype('f')
        #
        datatmp_4 = inter_dataA.argmax(2) + inter_dataA.argmin(2)
        data_4 = 0.5*datatmp_4.astype('f')
        #
        t = np.array([np.arange(0, Nt, 1)])
        datatmp_5 = self.inter_data.mean(0)
        datatmp_6 = datatmp_5.mean(0)
        ta = np.ones((2,Nt))
        for idx in range(Nt):
            ta[0,idx] = t[0,idx]
            ta[1,idx] = datatmp_6[idx]
            #
        #a_max = data_1.max()
        #a_min = data_1.min()
        #data_1N = (data_1 - a_min)/((a_max - a_min))

        # ADA code
        self.tmp_data = data_3
        self.on_ada_1()

        Nr = int(self.nb)
        ikey_tmp = []
        for ikey, ivalues in sorted(model.indcalls.iteritems()):
            ikey_tmp.append(ikey)
        Nc1 = len(ikey_tmp)
        ikey_tmp = []
        for ikey, ivalues in sorted(model.indmetrics.iteritems()):
            ikey_tmp.append(ikey)
        Nc2 = len(ikey_tmp)
        Nc = Nc1 + Nc2
        model.data = np.zeros((Nr,Nc),'float')
        for idx1 in range(Nr):
            model.data[idx1,0] = self.call[idx1]
            model.data[idx1,1] = self.feat_cx[idx1]
            model.data[idx1,2] = self.feat_cy[idx1]
            model.data[idx1,3] = self.feat_a1[idx1]
            model.data[idx1,4] = self.feat_bw[idx1]
            model.data[idx1,5] = self.feat_bh[idx1]
            model.data[idx1,6] = self.feat_a2[idx1]
            model.data[idx1,7] = self.feat_bx[idx1]
            model.data[idx1,8] = self.feat_by[idx1]
            model.data[idx1,9] = self.feat_bw[idx1]
            model.data[idx1,10] = self.feat_bh[idx1]
            model.data[idx1,11] = 1.0

        #self.populate_spreadsheet(self.view.output_grid, model.data)
        #self.populate_spreadsheet(self.view.output_grid2, model.data)
        #self.view.spreadsheet_nb.ChangeSelection(self.view.res_summary_page)

        # Store in res_outputdata
        model.res_outputdata = []
        model.res_outputdata.append(data_1)
        model.res_outputdata.append(data_2)
        model.res_outputdata.append(data_3)
        #self.res_outputdata.append(data_4)
        model.res_outputdata.append(ta)

        ############################################################################
        # To display tabular data after execution, set self._data to your output data
        # ADA Toolkit will load the NumPy array and display it automatically.
        # You can safely ignore this if you don't need to display data.
        self._data = model.data
        self.res_outputdata = model.res_outputdata
                #
        #self.res_outputdata = []
        #self.res_outputdata[1].dim = 2
        #self.res_outputdata[1].array = 10*np.random.rand(Nx,Ny)
        #
        # To display a text summary after execution, set self.results
        # ADA Toolkit will display this text in the text output field automatically.
        # You can safely ignore this if you don't need to display a text summary.
        self.results = "Sample ADA Model completed successfully."


    def load_rf(self):
        #"""loads data from selected .rf. file"""
        datafiledlg = tkFileDialog.askopenfilename(initialdir='/',  title='Please select a directory')

        #"""Code to Read .RF File into NDArray"""
        fidin=open(datafiledlg,"rb")
        header=array.array('l')
        header.fromfile(fidin,12)
        ny = header[3]
        nx = header[4]
        nt = header[5]

        nxyt = nx*ny*header[11]
        header2 = array.array('l')
        header2.fromfile(fidin,nxyt*2)
        wt_offset = header2[0:nxyt*2-2:2]
        wt_size = header2[1:nxyt*2-1:2]

        if header[7] == 4:
            data = np.zeros((ny,nx,nt),'l')
            datat = array.array('l')
        elif header[7]== 2:
            data = np.zeros((ny,nx,nt),'h')
            datat = array.array('h')
        else:
            data = np.zeros((ny,nx,nt),'B')
            datat = array.array('B')

        kk = -1
        for j1 in range(0, ny-1):
            for i1 in range(0, nx):
                kk = kk + 1
                fidin.seek(wt_offset[kk],0)
                datat.fromfile(fidin,wt_size[kk])
                data[j1,i1,:] = datat
                del datat[:]
        self.inter_data = data

        fidin.close()

    def on_ada_1(self):
        # 1) Get threshold and apply to amplitude data
        #str = self.textbox.GetValue()
        #self.threshold = map(float, str.split())
        #self.thresh2 = 2*self.threshold
        data1 = (self.tmp_data > 51)

        # 2) Pass data to temporary file
        filename = "imgtemp.png"
        data2 = data1.astype('uint8')
        image1 = Image.fromarray(data2)
        image1.save(filename)

        # 3) loads data to OpenCV
        image2 = cv2.imread(filename, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        # 4) find regions of interest using OpenCV FindContours algorithm
        contours, hierarchy = cv2.findContours( image2, cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)
        nb_cont = len(contours)
        self.nb = nb_cont
        self.contours = contours

        # 5) initial variables for ADA feature vectors
        self.feat_a1 = np.zeros(nb_cont,'float')
        self.feat_a2 = np.zeros(nb_cont,'float')
        self.feat_bx = np.zeros(nb_cont,'float')
        self.feat_by = np.zeros(nb_cont,'float')
        self.feat_bw = np.zeros(nb_cont,'float')
        self.feat_bh = np.zeros(nb_cont,'float')
        self.feat_cx = np.zeros(nb_cont,'float')
        self.feat_cy = np.zeros(nb_cont,'float')
        self.call = np.zeros(nb_cont,'float')
        #color = 'red'
        #attr1 = self.cellAttr = wx.grid.GridCellAttr()
        #attr1.SetBackgroundColour(color)
        #color = 'yellow'
        #attr2 = self.cellAttr = wx.grid.GridCellAttr()
        #attr2.SetBackgroundColour(color)

        # 6) store statistics for each region of interest (contour)
        i1 = 0;
        for contour in contours:
            # Evaluate area of regions of interest
            self.feat_a1[i1] = abs(cv2.contourArea(contour))
            # Evaluate bounding box of regions of interest
            feat_bbxy = cv2.boundingRect(contour)
            (feat_bbxy_x, feat_bbxy_y, feat_bbxy_width, feat_bbxy_height) = feat_bbxy
            self.feat_bx[i1] = feat_bbxy_x
            self.feat_by[i1] = feat_bbxy_y
            self.feat_bw[i1] = feat_bbxy_width
            self.feat_bh[i1] =  feat_bbxy_height
            # Evaluate centroid (and possibly higher order moments)
            moments1 = cv2.moments(contour)
            if moments1['m00'] != 0.0:
                self.feat_a2[i1] = moments1['m00']
                self.feat_cx[i1] = moments1['m10']/moments1['m00']
                self.feat_cy[i1] = moments1['m01']/moments1['m00']
                # Add logic to make call (default to 1 for now)
            self.call[i1] = 1
            # display call and feature measures in grid
            #self.grid.SetCellValue(i1,0, "%s" % self.call[i1])
            #self.grid.SetCellValue(i1,5, "%6.2f" % self.feat_bw[i1])
            # Increment index
            i1 = i1 + 1

    def plot0(self, axes_hdl, fig_hdl):
        """Generates global C-scan plot view."""
        # Example of plotting - if you have no primary plot, no need to define a plot1 method.
        #X = 10*np.random.rand(300,400)
        X = self.res_outputdata[0]
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