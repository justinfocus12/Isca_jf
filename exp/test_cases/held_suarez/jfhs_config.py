# functions to name output directories from parameter dictionaries
from os.path import join

def get_resolution_params():
    resolution_params = dict(
            horizontal = 'T21',
            vertical = 12, # number of z levels 
            temporal = 6, # hours per save 
            )
    return resolution_params

def get_ensemble_params()
    # Hours are the fundamental time unit 
    oneday = 24
    ensemble_params = dict(
            duration_spinup = 100*oneday,
            duration_max_chunk = 60*oneday, 
            duration_spinon = 50*oneday,
            n_chunk_spinoff = 6, # number of branches off the spinoff
            )
    return ensemble_params

def get_expt_name(resolution_params):
    expt_name = r"resH%sV%sT%s"%(
            resolution_params['horizontal'],
            resolution_params['vertical'],
            resolution_params['temporal'],
            )
    return expt_name

def get_output_dirs():
    resolution_params = get_resolution_params()
    expt_name = get_expt_name(resolution_params)
    expt_dir = join(
            "/net/scratch/jfinkel/proj-response/Isca_data/held_suarez",
            "2025-10-21",
            expt_name,
            )
    data_dir = join(expt_dir, "data")
    plot_dir = join(expt_dir, "plots")
    return data_dir, plot_dir


    

