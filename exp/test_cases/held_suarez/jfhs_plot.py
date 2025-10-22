import numpy as np
import xarray as xr
import maplotlib.pyplot as plt
from os import makedirs

import jfhs_config as cfg



def plot_temperature_snapshots(run_label):
    ensemble_params = cfg.get_resolution_params()
    data_dir,plot_dir = cfg.get_output_dirs()
    makedirs(plot_dir, exist_ok=True)
    resolution_params = cfg.get_resolution_params()
    n_save_per_day = 24 // resolution_params['temporal']
    ds = xr.open_dataset(join(data_dir,r'run%04d/atmos_%dhourly.nc'%(run_label,resolution_params['temporal'])), engine='netcdf4')
    

