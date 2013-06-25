# This import you need
from models.adatk_model import ADAModel
# Everything else depends on what your model requires
import numpy as np
from scipy.ndimage.filters import minimum_filter
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.filters import median_filter
from scipy.signal import hilbert
import wx

import bisect

import array
try:
    import Image
except ImportError: # Use alternate PIL module loading
    from PIL import Image

import cv2
from cv2 import cv

from models import dataio
import winspect
import utwin
from os.path import basename

# All ADA Models must be a subclass of ADAModel
class CompositeADABasic1(ADAModel):

    # All ADA Models must define the following information fields.
    name = "composites ADA basic 1"
    description = "Composites ADA  - Basic Model 1"
    authors = "Computational Tools and TRI/Austin, Inc."
    version = "1.2"
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

        ############################################################
        names_nam = []
        names_idx = []
        names_txt = []
        names_val = []
        names_dim = []
        names_des = []
        for ikey, ivalues in sorted(self.outputdata.iteritems()):
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

        ############################################################################
        for ikey, ivalues in sorted(self.inputdata.iteritems()):
            if ivalues['index'] == '1':
                filepath1 = ivalues['value']
        if filepath1 == '1':
            self.select_filename()
            filepath = self.filenm
        else:
            filepath = filepath1
            self.filenm = filepath1

        ############################################################################
        for ikey, ivalues in sorted(self.params.iteritems()):
            if ivalues['index'] == '1':
                para_dx1 = float(ivalues['value'])
            elif ivalues['index'] == '2':
                para_dy1 = float(ivalues['value'])
            elif ivalues['index'] == '3':
                para_da1 = float(ivalues['value'])
            elif ivalues['index'] == '4':
                para_th1 = float(ivalues['value'])
            elif ivalues['index'] == '5':
                para_th2 = float(ivalues['value'])
            elif ivalues['index'] == '6':
                para_th3 = float(ivalues['value'])
            elif ivalues['index'] == '7':
                para_th4 = float(ivalues['value'])
            elif ivalues['index'] == '8':
                para_df1 = float(ivalues['value'])
            elif ivalues['index'] == '9':
                para_df2 = float(ivalues['value'])
            elif ivalues['index'] == '10':
                para_ew1 = float(ivalues['value'])
            elif ivalues['index'] == '11':
                para_ew2 = float(ivalues['value'])
            elif ivalues['index'] == '12':
                para_cl = float(ivalues['value'])
            elif ivalues['index'] == '13':
                para_nlp = float(ivalues['value'])
            elif ivalues['index'] == '14':
                para_l12 = float(ivalues['value'])
            elif ivalues['index'] == '15':
                para_l23 = float(ivalues['value'])
            elif ivalues['index'] == '16':
                para_tp1 = float(ivalues['value'])
            elif ivalues['index'] == '17':
                para_tp2 = float(ivalues['value'])
            elif ivalues['index'] == '18':
                para_tp3 = float(ivalues['value'])

        ############################################################################
        #ext = ".rf"
        if ".rf" in filepath:
            self.load_rf()
            #
            self.para_a1 = 0.500  # %FSH or largest signal for frontwall / backwall calls = 64
            self.para_a2 = 0.500  # %FSH for second signal threshold (making feature calls) = 51
            self.para_a3 = 0.280  # %FSH for through thickness features (making feature calls) - defect features
            self.para_a4 = 0.500  # %drop from FSH for backwall signal
            self.para_t1 = 24 # time offset 1 - ringdown for front wall signal
            self.para_t2 = 9 # time offset 2 - ringdown before back wall signal
            self.para_c1 = 9 # 9 pixels in total area
            self.para_c2 = 3 # 3 pixels wide
            self.para_c3 = 3 # 3 pixels long
        #
        elif ".sdt" in filepath:
            self.load_sdt2()
            #
            self.para_a1 = 0.250  # %FSH or largest signal for frontwall / backwall calls = 64
            self.para_a2 = 0.199  # %FSH for second signal threshold (making feature calls) = 51
            self.para_a3 = 0.250  # %FSH for through thickness features (making feature calls) - defect features (0.180)
            self.para_a4 = 0.300  # %drop from FSH for backwall signal
            #self.para_t1 = 250 # time offset 1 - ringdown for front wall signal
            #self.para_t2 = 75 # time offset 2 - ringdown before back wall signal
            self.para_c1 = int(para_da1)  # 9 pixels in total area (= 4 by OpenCV math)
            self.para_c2 = int(para_dx1)  # 3 pixels wide
            self.para_c3 = int(para_dy1)  # 3 pixels long
        #
        elif ".csc" in filepath:
            self.load_csc()
            #
            #self.para_a1 = 0.200  # %FSH or largest signal for frontwall / backwall calls = 64
            #self.para_a2 = 0.398  # %FSH for second signal threshold (making feature calls) = 51
            #self.para_a3 = 0.280  # %FSH for through thickness features (making feature calls) - defect features
            #self.para_a4 = 0.500  # %drop from FSH for backwall signal
            #self.para_c1 = 9 # 9 pixels in total area
            #self.para_c2 = 3 # 3 pixels wide
            #self.para_c3 = 3 # 3 pixels long
            #
            self.para_a1 = para_th1  # %FSH or largest signal for frontwall / backwall calls = 64
            self.para_a2 = para_th2  # %FSH for second signal threshold (making feature calls) = 51
            self.para_a3 = para_th3  # %FSH for through thickness features (making feature calls) - defect features
            self.para_a4 = para_th4  # %drop from FSH for backwall signal
            self.para_c1 = int(para_da1)  # 9 pixels in total area (= 4 by OpenCV math)
            self.para_c2 = int(para_dx1)  # 3 pixels wide
            self.para_c3 = int(para_dy1)  # 3 pixels long
            #
        self.para_e0 = int(para_ew1) # = 3, radii associated with length criteria from edge to acreage portion of panels (1.2")
        self.para_e0a = int(round(0.707*self.para_e0)) # radii associated with length criteria from edge to acreage portion of panels (1.2")
        self.para_e1 = int(para_ew2) # = 15, radii associated with length criteria from edge to acreage portion of panels (1.2")
        self.para_e2 = int(round(0.707*self.para_e1)) # radii associated with length criteria from edge to acreage portion of panels (1.2")
        #
        Nx, Ny, Nt = self.inter_data.shape
        #
        datatmp_1mx = self.inter_data.max(2)
        datatmp_1mn = self.inter_data.min(2)
        #
        datatmp_1 = datatmp_1mx - datatmp_1mn
        #
        data_1 = datatmp_1.astype('f')
        #data_1 = data_1 - 128.0
        #
        datatmp_2 = self.inter_data.argmax(2) + self.inter_data.argmin(2)
        data_2 = 0.5*datatmp_2.astype('f')
        #
        # step 1a) call all transitions
        datatmp1mxa = datatmp_1mx.max(0)
        # can't assume -128!!!!!
        datatmp1mx = datatmp1mxa.max()
        #
        datatmp_1mx = 1.0*np.amax(self.inter_data)
        datatmp_1mn = 1.0*np.amin(self.inter_data)
        datatmp_1av = 1.0*np.mean(self.inter_data)
        datatmp_1pp = datatmp_1mx - datatmp_1mn
        datatmp_1p2 = 0.5*datatmp_1pp
        #
        self.para1x = np.round(self.para_a1*datatmp_1p2)
        self.para2x = np.round(self.para_a2*datatmp_1p2)
        self.para3x = np.round(self.para_a3*datatmp_1p2)
        self.para4x = np.round(self.para_a4*datatmp_1p2)
        #
        data_m0f = np.zeros((Nx,Ny))  # near surface map - TOF (1st cross)
        #
        ########################################
        # find first crossing for all signals
        for i1 in range(Nx):
            data_tm1 = np.fabs(self.inter_data[i1,:,:] - datatmp_1av) #- 128.0 # extract signal vector 1
            data_tmb = np.argmax(data_tm1 > self.para1x, 1)
            data_m0f[i1,:] = data_tmb
            #
        data_m0f_median = np.median(data_m0f, axis=None)
        data_m0f_slice = (data_m0f == data_m0f_median)
        #
        i0mx = np.sum(data_m0f_slice, axis=None)
        #
        if i0mx < (0.12*Nx*Ny):
            data_m0f_store = np.zeros((i0mx,Nt))
            #
            i0 = 0
            for i1 in range(Nx):
                for j1 in range(Ny):
                    if data_m0f_slice[i1,j1]:
                        datatmp_6 = self.inter_data[i1,j1,:] - datatmp_1av
                        data_m0f_store[i0,:] = np.abs(hilbert(datatmp_6))
                        i0 = i0 + 1
            datatmp_5 = self.inter_data.mean(0)
            datatmp_6 = datatmp_5.mean(0) - datatmp_1av
            datatmp_7 = data_m0f_store.mean(0)
        else:
            datatmp_5 = self.inter_data.mean(0)
            datatmp_6 = datatmp_5.mean(0) - datatmp_1av
            datatmp_7 = np.abs(hilbert(datatmp_6))

        ########################################
        # evaluate mean A-scan signal
        data_t0 = np.arange(Nt)  # extract time step vector 1
        t = np.array([np.arange(0, Nt, 1)])
        #
        ta = np.zeros((2,Nt))
        for idx in range(Nt):
            ta[0,idx] = t[0,idx]
            ta[1,idx] = datatmp_7[idx]
            #
        datatmp_7_max =  datatmp_7.max()
        datatmp_7_thr =  self.para_a1*datatmp_7_max

        ########################################
        # find width of pulse in time - metrics
        data_t1b = datatmp_7 > datatmp_7_thr
        data_tmp = data_t0[data_t1b] # (store first time step that exceeds threshold)
        i_a_fc = data_tmp[0]
        #
        data_t1b = datatmp_7[i_a_fc:] < (datatmp_7_thr)
        data_tmp = data_t0[data_t1b] # (store first time step that is below threshold)
        i_a_fd = data_tmp[0] + i_a_fc - 1
        #
        i_a_pp = np.argmax(datatmp_7[i_a_fc:i_a_fd])  # save - TOF map 1
        #
        #i_a_dp = i_a_pp + np.round(2*(i_a_pp - i_a_fc))
        #
        self.para_t1 = np.round(para_df2*(i_a_fd - i_a_fc + 1))
        self.para_t2 = np.round(para_df1*(i_a_pp))
        #
        ########################################
        # find bounds for front wall signal
        #data_t1 = np.fabs(datatmp_6 - datatmp_1av)
        #data_t1b = data_t1 > datatmp_7_thr
        #if data_t1b.size:
        #    data_tmp = data_t0[data_t1b] # (store first time step that exceeds threshold)
        #    i_a_zc = data_tmp[0]
        #else:
        #    i_a_zc = 0
        #i_a_avg = i_a_zc + self.para_t1
        #
        ########################################
        #
        data_m1a = np.zeros((Nx,Ny))  # near surface map - AMP (global)
        data_m1t = np.zeros((Nx,Ny))  # near surface map - TOF (1st cross)
        data_m1f = np.zeros((Nx,Ny))  # near surface map - TOF (1st cross)
        data_m2a = np.zeros((Nx,Ny))  # near surface map - AMP
        data_m2b = np.zeros((Nx,Ny))  # near surface map - TOF (1st cross)
        data_m2t = np.zeros((Nx,Ny))  # near surface map - TOF (peak)
        data_m3a = np.zeros((Nx,Ny))  # near surface map - AMP
        data_m3t = np.zeros((Nx,Ny))  # near surface map - TOF
        data_m4a = np.zeros((Nx,Ny))  # near surface map - AMP (backwall only)
        #
        data_m4t = np.zeros((Nx,Ny))  # near surface map - TOF (backwall only)
        data_m5a = np.zeros((Nx,Ny))  # near surface map - AMP (for testing)
        data_m6a = np.zeros((Nx,Ny))  # near surface map - AMP (for testing)
        #
        for i1 in range(Nx):
            for j1 in range(Ny):
                data_t1 = np.fabs(self.inter_data[i1,j1,:] - datatmp_1av) #- 128.0 # extract signal vector 1
                #data_t1 = data_tx.astype('f') - 128.0
                i_a_avg = data_m0f[i1,j1] + self.para_t1
                data_t1b = data_t1[:i_a_avg] > self.para1x # evaluate threshold vector 1
                data_tmp = data_t1[data_t1b] # (store first amplitude signal that exceeds threshold)
                if data_tmp.size:
                    #data_m1a[i1,j1] = data_tmp[0] # save - amplitude map 1
                    data_tmp = data_t0[data_t1b] # (store first time step that exceeds threshold)
                    i_a = data_tmp[0]
                    data_m1f[i1,j1] = 1.0*i_a  # save - TOF map 1
                    #
                    data_t1s = data_t1[:i_a_avg]
                    data_m1a[i1,j1] = data_t1s.max() # save - amplitude map 2
                    data_m1t[i1,j1] = data_t1s.argmax()  # save - TOF map 1
                    #
                    data_t2 = data_t1[(i_a+self.para_t1):] # extract vector 2 - thickness and backwall signals
                    if data_t2.size:
                        data_m2a[i1,j1] = data_t2.max() # save - amplitude map 2
                        data_m2b[i1,j1] = data_t2.argmax() # save - amplitude map 2
                        #
                        data_t02 = data_t0[(i_a+self.para_t1):] # extract time step vector 2
                        data_t2b = data_t2 > self.para2x # evaluate threshold vector 2
                        data_tmp = data_t02[data_t2b]
                        if data_tmp.size:
                            i_b = data_tmp[0]
                            data_m2t[i1,j1] = 1.0*i_b # save - amplitude map 1

        # check for missing data points with data at all neighbors
        data_m0f_store = np.zeros((4,Nt))
        for i1 in xrange(1,Nx-1):
            for j1 in  xrange(1,Ny-1):
                if data_m1a[i1,j1] <= self.para1x:
                    if ((data_m1a[i1-1,j1]>self.para1x) and (data_m1a[i1+1,j1]>self.para1x)):
                        if ((data_m1a[i1,j1-1]>self.para1x) and (data_m1a[i1,j1+1]>self.para1x)):
                            data_m0f_store[0,:] = self.inter_data[i1-1,j1,:]
                            data_m0f_store[1,:] = self.inter_data[i1+1,j1,:]
                            data_m0f_store[2,:] = self.inter_data[i1,j1-1,:]
                            data_m0f_store[3,:] = self.inter_data[i1,j1+1,:]
                            self.inter_data[i1,j1,:] = data_m0f_store.mean(0)
                            #
                            data_tm1 = np.fabs(data_m0f_store.mean(0) - datatmp_1av) #- 128.0 # extract signal vector 1
                            data_tmb = np.argmax(data_tm1 > self.para1x)
                            data_m0f[i1,j1] = data_tmb
                            #
                            # recalculate for previously missing data point
                            data_t1 = np.fabs(self.inter_data[i1,j1,:] - datatmp_1av) #- 128.0 # extract signal vector 1
                            #data_t1 = data_tx.astype('f') - 128.0
                            i_a_avg = data_m0f[i1,j1] + self.para_t1
                            data_t1b = data_t1[:i_a_avg] > self.para1x # evaluate threshold vector 1
                            data_tmp = data_t1[data_t1b] # (store first amplitude signal that exceeds threshold)
                            if data_tmp.size:
                                #data_m1a[i1,j1] = data_tmp[0] # save - amplitude map 1
                                data_m1a[i1,j1] = data_t1.max() # save - amplitude map 2
                                data_m1t[i1,j1] = data_t1.argmax()  # save - TOF map 1
                                #
                                data_tmp = data_t0[data_t1b] # (store first time step that exceeds threshold)
                                i_a = data_tmp[0]
                                data_m1f[i1,j1] = 1.0*i_a  # save - TOF map 1
                                #
                                data_t2 = data_t1[(i_a+self.para_t1):] # extract vector 2 - thickness and backwall signals
                                if data_t2.size:
                                    data_m2a[i1,j1] = data_t2.max() # save - amplitude map 2
                                    data_m2b[i1,j1] = data_t2.argmax() # save - amplitude map 2
                                    #
                                    data_t02 = data_t0[(i_a+self.para_t1):] # extract time step vector 2
                                    data_t2b = data_t2 > self.para2x # evaluate threshold vector 2
                                    data_tmp = data_t02[data_t2b]
                                    if data_tmp.size:
                                        i_b = data_tmp[0]
                                        data_m2t[i1,j1] = 1.0*i_b # save - amplitude map 1

        # through thickness threshold
        data1 = (data_m1a > self.para1x)
        data_f3 = data1.astype('f')
        #
        #data1 = (data_m1a > self.para1x)
        data_m5a = minimum_filter(data_f3,size=(1,self.para_e1))*minimum_filter(data_f3,size=(self.para_e1,1))
        data_m5a = data_m5a*minimum_filter(data_f3,size=(self.para_e2,self.para_e2))
        data_m5a = data_m5a + data_f3
        #
        data_m5b = minimum_filter(data_f3,size=(1,self.para_e0))*minimum_filter(data_f3,size=(self.para_e0,1))
        data_m5b = data_m5b*minimum_filter(data_f3,size=(self.para_e0a,self.para_e0a))
        data_m5a = data_m5a + data_m5b
        #for i1 in range(Nx):
        #    for j1 in range(Ny):
        #        data_m2a[i1,j1]=
        data_m4t = median_filter(data_m2t,size=(self.para_e1,self.para_e1))
        data_m4t2 = maximum_filter(data_m2t,size=(self.para_e1,self.para_e1))*(data_m5a >= 2)
        #data_m4t = np.maximum(data_m4t1,data_m4t2)
        data_m4t1 = (data_m4t==0)
        data_m4t[data_m4t1] = data_m4t2[data_m4t1]
        #data_m4t = np.putmask(data_m4t1,(data_m4t1==0),data_m4t2)
        #data_m4t[i1,j1] = data_t3.argmax()  # save - TOF map 3 (thickness only)
        #
        #data_median1_iny = np.zeros(Nx)
        data_median2_iny = np.zeros(Nx)
        #data_median1_inx = np.zeros(Ny)
        data_median2_inx = np.zeros(Ny)
        for i1 in range(Nx):
            #data_median1_iny[i1] = np.median(data_m1t[i1,:])
            data_median2_iny[i1] = np.median(data_m2t[i1,:])
            #
        for j1 in range(Ny):
            #data_median1_inx[j1] = np.median(data_m1t[:,j1])
            data_median2_inx[j1] = np.median(data_m2t[:,j1])
            #
        #data_median1_g = np.median(data_median1_inx)
        data_median2_g = np.median(data_median2_inx)

        for i1 in range(Nx):
            for j1 in range(Ny):
                data_t1 = np.fabs(self.inter_data[i1,j1,:] - datatmp_1av) # extract signal vector 1
                i_a = int(data_m1f[i1,j1] + self.para_t1)
                i_b = int(data_m4t[i1,j1] - self.para_t2)
                #i_b = int(data_median2_iny[i1] + data_median2_inx[j1] - data_median2_g - self.para_t1)
                if i_b <= i_a:
                    i_b = data_median2_g - self.para_t2
                if i_a > i_b:
                    i_a = i_b
                i_c = i_b + 1
                if i_c >= Nt:
                    i_c = Nt - 1
                #print("\ti_a:{0}".format(i_a))
                #print("\ti_b:{0}".format(i_b))
                #print("\ti_c:{0}".format(i_c))
                #
                data_t2 = data_t1[i_a:i_b] # extract vector 3 - thickness only
                if data_t2.size:
                    data_m3a[i1,j1] = data_t2.max() # save - pp amplitude map 3 (thickness only)
                    data_m3t[i1,j1] = data_t2.argmax()  # save - TOF map 3 (thickness only)
                    #
                    data_t3 = data_t1[i_c:] # extract vector 2 - thickness and backwall signals
                    if data_t3.size:
                        data_m4a[i1,j1] = data_t3.max() # save - amplitude map 4 (backwall only)
                        #data_m4t[i1,j1] = data_t3.argmax()  # save - TOF map 3 (thickness only)

        # revise through thickness amplitude results only for 'good' edges and acreage areas
        data_m3a =  data_m3a / ( data_m1a + 1) * (data_m5a >= 2)

        # revise backwall TOF based on frontwall TOF variation
        data_m4t =  data_m4t - data_m1t
        # revise backwall amplitude due to frontwall amplitude variation
        data_m6a =  data_m4a / ( data_m1a + 1) * (data_m5a >= 2)
        #
        data_m3m = np.ma.masked_where(data_m5a < 2,data_m3a)
        data_m6m = np.ma.masked_where(data_m5a < 2,data_m6a)
        data_m4m = np.ma.masked_where(data_m5a < 2,data_m4t)
        #
        Vppn_tt_median = np.ma.median(data_m3m)
        Vppn_bw_median = np.ma.median(data_m6m)
        TOF_bw_median = np.ma.median(data_m4m)
        #
        # through backwall drop threshold
        #data1 = (data_m4a < self.para4x)
        data1 = (data_m6a < self.para_a4) * (data_m5a >= 2)
        data_f1 = data1.astype('f')

        # through thickness threshold
        data1 = (data_m3a > self.para_a3)
        data_f2 = data1.astype('f')

        # Call ADA code - Step 2 (evaluate regions that match call criteria)
        self.tmp_data = np.logical_or((data_m6a < self.para_a4),(data_m3a > self.para_a3))* (data_m5a >= 2)
        self.tmp_data2 = data_m4a

        self.on_ada_1()

        Nr = int(self.nb)
        #
        ikey_tmp = []
        for ikey, ivalues in sorted(self.indcalls.iteritems()):
            ikey_tmp.append(ikey)
        Nc1 = len(ikey_tmp)
        ikey_tmp = []
        for ikey, ivalues in sorted(self.indmetrics.iteritems()):
            ikey_tmp.append(ikey)
        Nc2 = len(ikey_tmp)
        Nc = Nc1 + Nc2
        #
        if int(self.nb) == 0:
            Nr = 1
            self.nb = 1
            idx1 = 0
            self.feat_bx.append(1)
            self.feat_by.append(1)
            self.feat_bw.append(1)
            self.feat_bh.append(1)
            self.feat_cx.append(1)
            self.feat_cy.append(1)
            #
            model_data = np.zeros((Nr,Nc),'float')
            model_data[idx1,0] = 0.0
            model_data[idx1,1] = 0.0
            model_data[idx1,2] = 0.0
            model_data[idx1,3] = 0.0
            model_data[idx1,4] = 0.0
            model_data[idx1,5] = 0.0
            #
            model_data[idx1,6] = 0.0
            model_data[idx1,7] = 0.0
            model_data[idx1,8] = 0.0
            #
            model_data[idx1,9] = 0.0
            model_data[idx1,10] = 0.0
            model_data[idx1,11] = 0.0
        else:
            model_data = np.zeros((Nr,Nc),'float')
            for idx1 in range(Nr):
                model_data[idx1,0] = self.call[idx1]
                model_data[idx1,1] = self.feat_cx[idx1]
                model_data[idx1,2] = self.feat_cy[idx1]
                model_data[idx1,3] = self.feat_a1[idx1]
                model_data[idx1,4] = self.feat_bw[idx1]
                model_data[idx1,5] = self.feat_bh[idx1]
                #
                j1 = np.round(self.feat_cx[idx1])
                i1 = np.round(self.feat_cy[idx1])
                #
                model_data[idx1,0] = 2.0*data_f1[i1,j1] + data_f2[i1,j1]
                model_data[idx1,6] = data_m3t[i1,j1]
                model_data[idx1,7] = data_m3a[i1,j1]
                model_data[idx1,8] = data_m4a[i1,j1]
                #
                model_data[idx1,9] = self.feat_bx[idx1]
                model_data[idx1,10] = self.feat_by[idx1]
                model_data[idx1,11] = self.feat_a2[idx1]

        #self.populate_spreadsheet(self.view.output_grid, model.data)
        #self.populate_spreadsheet(self.view.output_grid2, model.data)
        #self.view.spreadsheet_nb.ChangeSelection(self.view.res_summary_page)
        #
        filename_2D = basename(filepath)
        #
        model_res_outputpara = []
        model_res_outputpara.append(filename_2D)
        model_res_outputpara.append(str(self.axis_x_resolution)+' '+self.axis_x_units)
        model_res_outputpara.append(str(self.axis_y_resolution)+' '+self.axis_y_units)
        model_res_outputpara.append(str(self.axis_time_resolution)+' '+self.axis_time_units)
        model_res_outputpara.append(str(datatmp_1p2))
        model_res_outputpara.append(str(self.para_t1))
        model_res_outputpara.append(str(self.para_t2))
        model_res_outputpara.append(str(Vppn_tt_median))
        model_res_outputpara.append(str(Vppn_bw_median))
        model_res_outputpara.append(str(TOF_bw_median))
        model_res_outputpara.append(str(self.nb))

        # Store in res_outputdata
        model_res_outputdata = []
        model_res_outputdata.append(data_m2a)
        model_res_outputdata.append(data_m2t)
        model_res_outputdata.append(data_m3a)
        model_res_outputdata.append(data_m3t)
        model_res_outputdata.append(data_m4a)
        model_res_outputdata.append(data_m1a)
        model_res_outputdata.append(data_m1t)
        model_res_outputdata.append(data_f1)
        model_res_outputdata.append(data_f2)
        model_res_outputdata.append(data_m0f)  #change from data_f3
        model_res_outputdata.append(data_m4t)
        model_res_outputdata.append(data_m5a)
        model_res_outputdata.append(data_m6a)
        model_res_outputdata.append(ta)
        #
        filename_2D_long = filename_2D + '.met'
        thefile = open(filename_2D_long, 'w')
        for item in model_res_outputpara:
            thefile.write("%s\n" % item)
        #np.savetxt(filename_2D_long, model_res_outputpara, delimiter=",")
        thefile.close()
        #
        filename_2D_long = 'validation_study.met'
        thefile = open(filename_2D_long, 'a')
        item = ",".join(model_res_outputpara)
        thefile.write("%s\n" % item)
        thefile.close()
        #
        filename_2D_long = 'validation_study.ind'
        thefile = open(filename_2D_long, 'a')
        #
        for idx1 in range(Nr):
            #
            model_res_outputind = []
            model_res_outputind.append(filename_2D)
            model_res_outputind.append(str(idx1))
            #
            model_res_outputind.append(str(model_data[idx1,0]))
            model_res_outputind.append(str(model_data[idx1,1]))
            model_res_outputind.append(str(model_data[idx1,2]))
            model_res_outputind.append(str(model_data[idx1,3]))
            model_res_outputind.append(str(model_data[idx1,4]))
            model_res_outputind.append(str(model_data[idx1,5]))
            model_res_outputind.append(str(model_data[idx1,6]))
            model_res_outputind.append(str(model_data[idx1,7]))
            model_res_outputind.append(str(model_data[idx1,8]))
            model_res_outputind.append(str(model_data[idx1,9]))
            model_res_outputind.append(str(model_data[idx1,10]))
            model_res_outputind.append(str(model_data[idx1,11]))
            #
            item = ",".join(model_res_outputind)
            thefile.write("%s\n" % item)
        thefile.close()
        #
        filename_2D_long = filename_2D + '.ind'
        np.savetxt(filename_2D_long, model_data, delimiter=",")
        #
        for idx1 in range(Nf-1):
            filename_2D_long = filename_2D + outputdata_val[idx1]
            a = model_res_outputdata[idx1]
            np.savetxt(filename_2D_long, a, delimiter=",")
        #
        model_res_inddata1 = []
        model_res_inddata2 = []
        model_res_inddata3 = []
        model_res_inddata4 = []
        for idx1 in range(Nr):
            ix0 = np.round(self.feat_cx[idx1])
            iy0 = np.round(self.feat_cy[idx1])
            ix1 = np.round(self.feat_bx[idx1])
            iy1 = np.round(self.feat_by[idx1])
            ix2 = ix1 + 1 + np.round(self.feat_bw[idx1])
            iy2 = iy1 + 1 + np.round(self.feat_bh[idx1])
            data_i1 = data_m2a[iy1:iy2][:,ix1:ix2]
            data_i2 = data_m2t[iy1:iy2][:,ix1:ix2]
            data_i3 = data_m3a[iy1:iy2][:,ix1:ix2]
            #
            data_i5 = self.inter_data[iy0,ix0,:]  # extract signal vector (- 128.0)
            data_i4 = np.zeros((2,Nt))
            for idx2 in range(Nt):
                data_i4[0,idx2] = t[0,idx2]
                data_i4[1,idx2] = data_i5[idx2]
            #data_i1 = np.array( [[2,0,4],[3,4,4],[3,4,7]] )
            #data_i2 = np.array( [[5,4,2],[1,2,2],[3,4,1]] )
            #data_i3 = np.array( [[-1,2,7],[-4,1,8],[1,1,1]] )
            #data_i4 = np.array( [[1,2,3,4],[20,30,40,50]] )
            #
            model_res_inddata1.append(data_i1)
            model_res_inddata2.append(data_i2)
            model_res_inddata3.append(data_i3)
            model_res_inddata4.append(data_i4)
        model_res_inddata = []
        model_res_inddata.append(model_res_inddata1)
        model_res_inddata.append(model_res_inddata2)
        model_res_inddata.append(model_res_inddata3)
        model_res_inddata.append(model_res_inddata4)

        ############################################################################
        # To display tabular data after execution, set self._data to your output data
        # ADA Toolkit will load the NumPy array and display it automatically.
        # You can safely ignore this if you don't need to display data.
        #model_data_str = ["%.2f" % x for x in model_data.reshape(model_data.size)]
        #model_data_str = model_data_str.reshape(model_data.shape)
        model_data_str = model_data.tolist()
        for idx1 in range(Nr):
            idx = model_data_str[idx1][0]
            if idx == 0:
                model_data_str[idx1][0] = "IND"
            elif idx == 1:
                model_data_str[idx1][0] = "TT+"
            elif idx == 2:
                model_data_str[idx1][0] = "BW-"
            elif idx == 3:
                model_data_str[idx1][0] = "TT+,BW-"
            for idx2 in range(1,12):
                #tmp_val = str(model_data_str[idx1][idx2])
                tmp_val = "{0:.3f}".format(model_data_str[idx1][idx2])
                model_data_str[idx1][idx2] = tmp_val

        #model_data_str = map(str,model_data)
        self._data = model_data_str
        #self._data = model_data
        self.res_outputdata = model_res_outputdata
        self.res_outputpara = model_res_outputpara
        self.res_inddata = model_res_inddata
        #
        #self.res_outputdata = []
        #self.res_outputdata[1].dim = 2
        #self.res_outputdata[1].array = 10*np.random.rand(Nx,Ny)
        #
        # To display a text summary after execution, set self.results
        # ADA Toolkit will display this text in the text output field automatically.
        # You can safely ignore this if you don't need to display a text summary.
        self.results = "Sample ADA Model completed successfully."

    def select_filename(self):
        #"""loads data from selected .rf. file"""
        #datafiledlg = tkFileDialog.askopenfilename(initialdir='/',  title='Please select a directory')
        dlg = wx.FileDialog(None, message="Open Data File...", defaultDir='/', defaultFile="",
            wildcard = "Data files (*.rf;*.csc;*.sdt;*.tif)|*.rf;*.csc;*.sdt;*.tif", style=wx.OPEN)
        # wildcard = ".RF files (*.rf)|*.rf|.CSC files (*.csc)|*.csc|.SDT files (*.sdt)|*.sdt"
        if dlg.ShowModal() == wx.ID_OK:
            datafiledlg = dlg.GetPath()
        dlg.Destroy() # we don't need the dialog any more so we ask it to clean-up
        self.filenm = datafiledlg

    def load_rf(self):
        #"""loads data from selected .rf. file"""
        ##datafiledlg = tkFileDialog.askopenfilename(initialdir='/',  title='Please select a directory')
        #dlg = wx.FileDialog(None, message="Open .rf File...", defaultDir='/', defaultFile="",
        #    wildcard = ".RF files (*.rf)|*.rf", style=wx.OPEN)
        #if dlg.ShowModal() == wx.ID_OK:
        #    datafiledlg = dlg.GetPath()
        #dlg.Destroy() # we don't need the dialog any more so we ask it to clean-up
        datafiledlg = self.filenm

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
            data = np.zeros((ny-1,nx,nt),'l')
            datat = array.array('l')
        elif header[7]== 2:
            data = np.zeros((ny-1,nx,nt),'h')
            datat = array.array('h')
        else:
            data = np.zeros((ny-1,nx,nt),'B')
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

    def load_sdt2(self):

        datafiledlg = self.filenm
        #
        tst = winspect.DataFile(datafiledlg)
        tst.read_data()
        #
        self.axis_x_resolution = tst.axes[0].resolution
        self.axis_x_sample_points = tst.axes[0].sample_points
        self.axis_x_units = tst.axes[0].units
        #
        self.axis_y = None
        self.axis_y_resolution = tst.axes[1].resolution
        self.axis_y_sample_points = tst.axes[1].sample_points
        self.axis_y_units = tst.axes[1].units
        #
        for subset in tst.datasets:
            if 'waveform' in subset.data_type:
                self.inter_data = subset.data
                self.axis_time = None
                self.axis_time_resolution = subset.resolution
                self.axis_time_sample_points = subset.sample_points
                self.axis_time_units = subset.time_units

    def load_sdt(self):
        #"""loads data from selected .sdt. file"""
        #dlg = wx.FileDialog(None, message="Open .sdt File...", defaultDir='/', defaultFile="",
        #    wildcard = ".SDT files (*.sdt)|*.sdt", style=wx.OPEN)
        #if dlg.ShowModal() == wx.ID_OK:
        #    datafiledlg = dlg.GetPath()
        #dlg.Destroy() # we don't need the dialog any more so we ask it to clean-up
        datafiledlg = self.filenm

        #"""Code to Read .RF File into NDArray"""
        #fid = fopen(filename,permission,machineformat);
        fidin=open(datafiledlg,"rb")

        for k in range(48):
            tline = fidin.readline()
            if k == 6:
                str_tmp1 = tline[34:]
                nx = int(str_tmp1)
            elif k == 10:
                str_tmp1 = tline[34:]
                ny = int(str_tmp1)
            elif k == 39:
                str_tmp1 = tline[34:]
                nt = int(str_tmp1)
            elif k == 41:
                str_tmp1 = tline[34:41]
                dt = float(str_tmp1)
        fidin.close()

        with open(datafiledlg,"rb") as fidin:
            header_line = fidin.readline()
            while True:
                if "|^Data Set^|" in header_line:
                    data_offset = fidin.tell()
                    break
                header_line = fidin.readline()
        fidin.close()

        fidin=open(datafiledlg,"rb")
        fidin.seek(data_offset)

        #nxyt = nx*ny*header[11]
        #header2 = array.array('l')
        #header2.fromfile(fidin,nxyt*2)
        #wt_offset = header2[0:nxyt*2-2:2]
        #wt_size = header2[1:nxyt*2-1:2]
        data = np.zeros((ny,nx,nt),'l')
        #
        #data = fread(fid,inf,'schar');
        nyx = ny*nx
        datat = fidin.read(nyx)
        datat = fidin.read(nyx)
        #
        kk = 0
        for j1 in range(ny):
            for i1 in range(nx):
                #kk = kk + 1
                #kknt = nt*(kk-1)
                #datat = fidin.read(nt)
                datat = np.fromfile(fidin, dtype=np.int8, count=nt)
                data[j1,i1,:] = datat + 128.0
        #
        self.inter_data = data
        #
        fidin.close()

    def load_csc(self):
        #"""loads data from selected .csc. file"""
        #datafiledlg = self.filenm
        #"""Code to Read .RF File into NDArray"""
        #fidin=open(datafiledlg,"rb")
        #
        raw_data = dataio.get_utwin_data(self.filenm)
        for dataset in raw_data:
            if dataset == 'waveform':
                self.inter_data = raw_data[dataset][0]

        #
        #self.axis_x_resolution = tst.axes[0].resolution
        #self.axis_x_sample_points = tst.axes[0].sample_points
        #self.axis_x_units = tst.axes[0].units
        #
        scan_prop = dataio.get_utwin_prop(self.filenm)
        for field in scan_prop:
            if field == 'n_height':
                self.axis_x_sample_points = scan_prop[field]
            if field == 'cs_index_resolution':
                self.axis_x_resolution = scan_prop[field]
            if field == 'n_width':
                self.axis_y_sample_points = scan_prop[field]
            if field == 'cs_scan_resolution':
                self.axis_y_resolution = scan_prop[field]
            if field == 'rf_dt':
                self.axis_time_resolution = scan_prop[field]
        #
        self.axis_x_units = "in"
        self.axis_y_units = "in"
        self.axis_time_units = "us"
        #
        self.axis_y = None
        self.axis_time = None

    def on_ada_1(self):
        # 1) Get threshold and apply to amplitude data
        #str = self.textbox.GetValue()
        #self.threshold = map(float, str.split())
        #self.thresh2 = 2*self.threshold
        data1 = (self.tmp_data)
        #data1 = (self.tmp_data > self.para3x)
        #data1b = (self.tmp_data2 > self.para4x)
        #data1 = np.logical_or(data1a,data1b)

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
        #
        contours = sorted(contours, key=lambda contour:cv2.contourArea(contour), reverse=True)
        # 5) initial variables for ADA feature vectors
        #self.feat_a1 = np.zeros(nb_cont,'float')
        #self.feat_a2 = np.zeros(nb_cont,'float')
        #self.feat_bx = np.zeros(nb_cont,'float')
        #self.feat_by = np.zeros(nb_cont,'float')
        #self.feat_bw = np.zeros(nb_cont,'float')
        #self.feat_bh = np.zeros(nb_cont,'float')
        #self.feat_cx = np.zeros(nb_cont,'float')
        #self.feat_cy = np.zeros(nb_cont,'float')
        #self.call = np.zeros(nb_cont,'float')
        self.feat_a1 = []
        self.feat_a2 = []
        self.feat_bx = []
        self.feat_by = []
        self.feat_bw = []
        self.feat_bh = []
        self.feat_cx = []
        self.feat_cy = []
        self.call = []

        #color = 'red'
        #attr1 = self.cellAttr = wx.grid.GridCellAttr()
        #attr1.SetBackgroundColour(color)
        # 6) store statistics for each region of interest (contour)
        i1 = 0;
        for contour in contours:
            # Evaluate area of regions of interest
            # Evaluate bounding box of regions of interest
            feat_area = abs(cv2.contourArea(contour))
            feat_bbxy = cv2.boundingRect(contour)
            (feat_bbxy_x, feat_bbxy_y, feat_bbxy_width, feat_bbxy_height) = feat_bbxy
            #
            if feat_area >= self.para_c1:
                if feat_bbxy_x >= self.para_c2:
                    if feat_bbxy_y >= self.para_c3:
                        # save area feature
                        self.feat_a1.append(feat_area)
                        # save dimension features
                        self.feat_bx.append(feat_bbxy_x)
                        self.feat_by.append(feat_bbxy_y)
                        self.feat_bw.append(feat_bbxy_width)
                        self.feat_bh.append(feat_bbxy_height)
                        # Evaluate centroid (and possibly higher order moments)
                        moments1 = cv2.moments(contour)
                        if moments1['m00'] != 0.0:
                            self.feat_a2.append(moments1['m00'])
                            self.feat_cx.append(moments1['m10']/moments1['m00'])
                            self.feat_cy.append(moments1['m01']/moments1['m00'])
                            # Add logic to make call (default to 1 for now)
                        self.call.append(1.0)
                        i1 = i1 + 1
            # display call and feature measures in grid
            #self.grid.SetCellValue(i1,0, "%s" % self.call[i1])
            #self.grid.SetCellValue(i1,5, "%6.2f" % self.feat_bw[i1])
            # Increment index
        self.nb = i1

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
        Nr1 = len(self._data)
        for idx in range(Nr1):
            xc = self._data[idx][1]
            yc = self._data[idx][2]
            tc = str(idx+1)
            axes_hdl.text(xc,yc,tc)
            #
        #axes_hdl.set_title("C-scan")
        axes_hdl.set_xlabel("X Axis")
        axes_hdl.set_ylabel("Y Axis")
        #
        #axes_hdl.xlims = axes_hdl.get_xlim()
        #axes_hdl.ylims = axes_hdl.get_ylim()

    def plot1(self, axes_hdl, fig_hdl):
        """Generates the primary plot on the specified matplotlib Axes instance."""
        #
        #if self.res_inddata[0][0]:
        X = self.res_inddata[0][0]
        #
        axes_hdl.clear()
        fig_hdl.clear() #in case there are extra axes like colorbars
        axes_hdl = fig_hdl.add_subplot(111, navigate=True)
        #
        cax = axes_hdl.imshow(X)
        fig_hdl.colorbar(cax)
        #
        axes_hdl.set_xlabel("X Axis")
        axes_hdl.set_ylabel("Y Axis")
        # Example of plotting - if you have no primary plot, no need to define a plot1 method.
        #axes_hdl.plot([1,2,3,4], [1,4,9,16], 'ro')
        #axes_hdl.axis([0, 6, 0, 20])
        #axes_hdl.set_title("Example Plot 1")
        #axes_hdl.set_xlabel("X Axis")
        #axes_hdl.set_ylabel("Y Axis")

    def plot2(self, axes_hdl, fig_hdl):
        """Generates the secondary plot on the specified matplotlib Axes instance."""
        #
        #if self.res_inddata[1][0]:
        X = self.res_inddata[1][0]
        #
        axes_hdl.clear()
        fig_hdl.clear() #in case there are extra axes like colorbars
        axes_hdl = fig_hdl.add_subplot(111, navigate=True)
        #
        cax = axes_hdl.imshow(X)
        fig_hdl.colorbar(cax)
        #
        axes_hdl.set_xlabel("X Axis")
        axes_hdl.set_ylabel("Y Axis")
        # Example of plotting - if you have no secondary plot, no need to define a plot2 method.
        #t = np.arange(0., 5., 0.2)
        #axes_hdl.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^')
        #axes_hdl.set_title("Example Plot 2")
        #axes_hdl.set_xlabel("X Axis")
        #axes_hdl.set_ylabel("Y Axis")
        #axes_hdl.legend(("Linear", "Square", "Cubic"), 'upper right', title="Functions", shadow=True, fancybox=True)