import numpy as np
import xarray as xr
import cftime
import datetime as dtlib
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

def datetime_from_cftime(tc):
    return dtlib.datetime(year=tc.year, month=tc.month, day=tc.day, hour=tc.hour) 
    #**dict({timedivision: getattr(tc, timedivision) for timedivision in ['year','month','day','hour']}))

def load_ensemble_member(run_label, data_dir):
    resolution_params = cfg.get_resolution_params()
    ds = xr.open_dataset(join(data_dir,r'run%04d/atmos_%dhourly.nc'%(run_label,resolution_params['temporal'])), engine='netcdf4')
    print(f'{ds.time.values[:10] = }')
    print(f'{ds.time[0].item() = }')
    return ds

def plot_temperature_snapshots(ds, run_label, plot_dir):
    # --------- temperature heatmaps on 3 consecutive days ------------
    for i_time in range(3):
        fig,ax = plt.subplots()
        xr.plot.pcolormesh(ds['temp'].isel(pfull=-1,time=i_time), x='lon', y='lat', cmap=plt.cm.coolwarm)
        ax.set_xlabel('Lon')
        ax.set_ylabel('Lat')
        print(f'{ds.time.values[0] = }')
        ax.set_title(f'Surf. Temp. %s'%(ds.time.values[i_time].strftime('%Y-%m-%d')))
        fig.savefig(join(plot_dir, r'tas_run%d_itime%d'%(run_label,i_time)), **pltkwargs)
        plt.close(fig)
    return

def plot_temperature_timeseries(dss, plot_dir):
    # Use time coordinate to our advantage to put all on a spaghetti plot
    resolution_params = cfg.get_resolution_params()
    ensemble_params = cfg.get_ensemble_params()
    t0 = dtlib.datetime(**ensemble_params['current_date'])
    fig,ax = plt.subplots()
    for ds in dss:
        print(ds.time.values[0])
        i_lon = np.argmin(np.abs(ds.lon.data - 180.0))
        i_lat = np.argmin(np.abs(ds.lat.data - 45.0)) 
        temp = ds['temp'].isel(lon=i_lon, lat=i_lat, pfull=-1)
        t1 = datetime_from_cftime(ds['time'][0].item())
        dt1 = (t1 - t0).days
        ax.plot(dt1+np.arange(ds.time.size)*resolution_params['temporal']/24, temp.to_numpy())
        ax.set_xlabel('Days since %s'%(t1.strftime('%Y-%m-%d')))
    ax.set_ylabel('Surf. Temp.')
    ax.set_xlabel('Time')
    fig.savefig(join(plot_dir, r'tas_loc.png'), **pltkwargs)
    plt.close(fig)
    return



def main():
    # --------- set up plot directory ---------
    data_dir,plot_dir = cfg.get_output_dirs()
    makedirs(plot_dir, exist_ok=True)
    dss = []
    for run_label in range(1,4):
        ds = load_ensemble_member(run_label, data_dir)
        dss.append(ds)
        plot_temperature_snapshots(ds, run_label, plot_dir)
    plot_temperature_timeseries(dss, plot_dir)

if __name__ == "__main__":
    main()




    

