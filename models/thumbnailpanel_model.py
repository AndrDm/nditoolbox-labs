''' thumbnailpanel_model.py - Model for the ThumbnailPanel control

Chris R. Coughlin (TRI/Austin, Inc.)
'''

__author__ = 'Chris R. Coughlin'

from controllers import pathfinder
import wx
import matplotlib
import matplotlib.cm as cm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import hashlib
from multiprocessing import Process, Pipe
import os.path
import StringIO

def get_data(data_fname, **import_params):
    '''Loads the data from an ASCII-delimited text file'''
    comment_char = import_params.get('commentchar', '#')
    delim_char = import_params.get('delimiter', None)
    header_lines = import_params.get('skipheader', 0)
    footer_lines = import_params.get('skipfooter', 0)
    cols_to_read = import_params.get('usecols', None)
    transpose_data = import_params.get('transpose', False)
    data = np.genfromtxt(data_fname, comments=comment_char, delimiter=delim_char,
        skip_header=header_lines, skip_footer=footer_lines, usecols=cols_to_read,
        unpack=transpose_data)
    return data

def create_plot(data, title, width, height):
    '''Generates a matplotlib Figure instance of the specified data'''
    matplotlib.rcParams['axes.formatter.limits'] = -4, 4
    matplotlib.rcParams['font.size'] = 9
    matplotlib.rcParams['axes.titlesize'] = 9
    matplotlib.rcParams['axes.labelsize'] = 9
    matplotlib.rcParams['xtick.labelsize'] = 8
    matplotlib.rcParams['ytick.labelsize'] = 8
    figure = Figure(figsize=(width, height))
    canvas = FigureCanvas(figure)
    axes = figure.gca()
    if 2 in data.shape:
        axes.plot(data[0], data[1])
    elif data.ndim==1:
        axes.plot(data)
    else:
        img = axes.imshow(data, cmap=cm.get_cmap('Spectral'))
        figure.colorbar(img)
    axes.set_title(title)
    axes.grid(True)
    return figure

def plot_stream(data, title, width, height):
    '''Returns a StringIO stream of the data plot'''
    img_stream = StringIO.StringIO()
    figure = create_plot(data, title, width, height)
    figure.savefig(img_stream, format='png')
    img_stream.seek(0)
    return img_stream

def plot_pipe(data, title, width, height, pipe):
    '''Writes the PNG StringIO stream of the specified data's plot
    to the specified pipe.  Primarily intended for multiprocessing.'''
    img_stream = plot_stream(data, title, width, height)
    pipe.send(img_stream)
    pipe.close()

def plot(data_filename, width, height, **import_params):
    '''Returns a PNG plot of the specified data file's dataset'''
    data = get_data(data_filename, **import_params)
    return gen_thumbnail(plot_stream(data,
                                     os.path.basename(data_filename),
                                     width, height),
                         data_filename)

def multiprocess_plot(data_filename, width, height, **import_params):
    '''Spawns a subprocess to generate the plot, and returns the result as a PNG wxBitmap.
    The result is also saved to the thumbnails folder for reuse.'''
    data = get_data(data_filename, **import_params)
    in_conn, out_conn = Pipe()
    plot_proc = Process(target=plot_pipe,
                        args=(data, os.path.basename(data_filename), width, height, out_conn))
    plot_proc.start()
    img_stream = in_conn.recv()
    plot_proc.join()
    return gen_thumbnail(img_stream, data_filename)

def gen_thumbnail(image_stream, data_filename):
    '''Returns a wxBitmap of the given image stream.  If the bitmap doesn't exist
    in the thumbnails folder it is saved there for reuse'''
    img = wx.ImageFromStream(image_stream, type=wx.BITMAP_TYPE_PNG)
    thumb_fn = thumbnail_name(data_filename)
    if not os.path.exists(thumb_fn):
        with open(thumb_fn, 'wb') as img_file:
            # Cache the PNG for reuse
            img.SaveStream(img_file, type=wx.BITMAP_TYPE_PNG)
    return wx.BitmapFromImage(img)

def thumbnail_name(data_filename):
    '''Returns the name of the thumbnail corresponding to the specified data file.'''
    m = hashlib.md5(data_filename)
    return os.path.join(pathfinder.thumbnails_path(), m.hexdigest() + '.png')