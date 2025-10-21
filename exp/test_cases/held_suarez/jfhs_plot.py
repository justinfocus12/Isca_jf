import numpy as np
import xarray as xr
import maplotlib.pyplot as plt

import jfhs_config as cfg

resolution_params = cfg.get_resolution_params()
ensemble_params = cfg.get_resolution_params()
data_dir,plot_dir = cfg.get_output_dirs()


