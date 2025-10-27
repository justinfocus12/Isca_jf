# functions to name output directories from parameter dictionaries
from os.path import join
from collections import namedtuple

def get_resolution_params():
    resolution_params = dict(
            horizontal = 'T21',
            vertical = 12, # number of z levels 
            temporal = 6, # hours per save 
            )
    return resolution_params


def get_ensemble_params():
    # Hours are the fundamental time unit 
    oneday = 24
    current_date = dict(year=2000, month=1, day=1, hour=0, second=0, microsecond=0)
    ensemble_params = dict(
            duration_spinup = 40*oneday,
            duration_chunk_max = 30*oneday, 
            duration_spinon = 20*oneday,
            duration_spinoff = 25*oneday,
            n_spinoff = 0, # number of branches off the spinoff
            current_date = current_date,
            )
    return ensemble_params

def get_expt_name(resolution_params):
    expt_name = r"resH%sV%sT%s"%(
            resolution_params['horizontal'],
            resolution_params['vertical'],
            resolution_params['temporal'],
            )
    return "_".join([get_date_str(), expt_name])

def get_date_str():
    return '2025-10-28'


def get_output_dirs():
    resolution_params = get_resolution_params()
    expt_name = get_expt_name(resolution_params)
    expt_dir = join(
            "/net/scratch/jfinkel/proj-response/Isca_data/",
            expt_name,
            )
    data_dir = expt_dir # If want to change this, must move output from the module's default folder
    plot_dir = join(expt_dir, "plots")
    return data_dir, plot_dir


    

