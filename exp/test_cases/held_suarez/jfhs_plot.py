import numpy as np
import xarray as xr
from matplotlib import pyplot as plt, rcParams
from os import makedirs
from os.path import join, exists
import sys

rcParams['font.family'] = 'monospace'
pltkwargs = dict({
    'bbox_inches': 'tight',
    'pad_inches': 0.02,
    })

import jfhs_config as cfg

def load_ensemble_member(run_label, data_dir):
    resolution_params = cfg.get_resolution_params()
    ds = xr.open_dataset(join(data_dir,r'run%04d/atmos_%dhourly.nc'%(run_label,resolution_params['temporal'])), engine='netcdf4')
    return ds

def plot_temperature_snapshots(ds, run_label, plot_dir):
    # --------- temperature heatmaps on 3 consecutive days ------------
    for i_time in range(3):
        fig,ax = plt.subplots()
        xr.plot.pcolormesh(ds['temp'].isel(pfull=-1,time=i_time), x='lon', y='lat', cmap=plt.cm.coolwarm)
        ax.set_xlabel('Lon')
        ax.set_ylabel('Lat')
        ax.set_title(f'Surf. Temp. %s'%(ds.time[i_time].item().strftime()))
        fig.savefig(join(plot_dir, r'tas_run%d_itime%d'%(run_label,i_time)), **pltkwargs)
        plt.close(fig)
    return

def plot_temperature_timeseries(dss, data_dir, plot_dir):
    # Use time coordinate to our advantage to put all on a spaghetti plot
    pass


def main():
    # --------- set up plot directory ---------
    data_dir,plot_dir = cfg.get_output_dirs()
    makedirs(plot_dir, exist_ok=True)
    for run_label in range(1,4):
        ds = load_ensemble_member(run_label, data_dir)
        plot_temperature_snapshots(ds, run_label, plot_dir)

if __name__ == "__main__":
    main()




    

