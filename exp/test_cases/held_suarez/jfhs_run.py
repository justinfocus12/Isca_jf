import numpy as np
import xarray as xr

from isca import DryCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

import jfhs_config as cfg

def build_experiment():

    resolution_params = cfg.get_resolution_params()
    ensemble_params = cfg.get_ensemble_params()
    data_dir,plot_dir = cfg.get_output_dirs()
    
    # a CodeBase can be a directory on the computer,
    # useful for iterative development
    cb = DryCodeBase.from_directory(GFDL_BASE)
    
    # or it can point to a specific git repo and commit id.
    # This method should ensure future, independent, reproducibility of results.
    # cb = DryCodeBase.from_repo(repo='https://github.com/isca/isca', commit='isca1.1')
    
    # compilation depends on computer specific settings.  The $GFDL_ENV
    # environment variable is used to determine which `$GFDL_BASE/src/extra/env` file
    # is used to load the correct compilers.  The env file is always loaded from
    # $GFDL_BASE and not the checked out git repo.
    
    # create an Experiment object to handle the configuration of model parameters
    # and output diagnostics
    
    exp_name = cfg.get_expt_name(resolution_params)
    exp = Experiment(exp_name, codebase=cb)
    
    #Tell model how to write diagnostics
    diag = DiagTable()
    n_save_per_day = 24 // resolution_params['temporal']
    diag.add_file(f'atmos_{n_save_per_day}xday', resolution_params['temporal'], time_units='hours' )
    
    #Tell model which diagnostics to write
    diag.add_field('dynamics', 'ps', time_avg=False)
    diag.add_field('dynamics', 'bk')
    diag.add_field('dynamics', 'pk')
    diag.add_field('dynamics', 'ucomp', time_avg=False)
    diag.add_field('dynamics', 'vcomp', time_avg=False)
    diag.add_field('dynamics', 'temp', time_avg=False)
    diag.add_field('dynamics', 'vor', time_avg=False)
    diag.add_field('dynamics', 'div', time_avg=False)
    
    exp.diag_table = diag
    
    # define namelist values as python dictionary
    # wrapped as a namelist object.
    namelist = Namelist({
        'main_nml': {
            'dt_atmos': 600,
            'days': ensemble_params['duration_chunk_max'],
            'calendar': 'thirty_day',
            'current_date': [2000,1,1,0,0,0] # but does this get replaced from one run to the next? 
        },
    
        'atmosphere_nml': {
            'idealized_moist_model': False  # False for Newtonian Cooling.  True for Isca/Frierson
        },
    
        'spectral_dynamics_nml': {
            'damping_order'           : 4,                      # default: 2
            'water_correction_limit'  : 200.e2,                 # default: 0
            'reference_sea_level_press': 1.0e5,                  # default: 101325
            'valid_range_t'           : [100., 800.],           # default: (100, 500)
            'initial_sphum'           : 0.0,                  # default: 0
            'vert_coord_option'       : 'uneven_sigma',         # default: 'even_sigma'
            'scale_heights': 6.0,
            'exponent': 7.5,
            'surf_res': 0.5
        },
    
        # configure the relaxation profile
        'hs_forcing_nml': {
            't_zero': 315.,    # temperature at reference pressure at equator (default 315K)
            't_strat': 200.,   # stratosphere temperature (default 200K)
            'delh': 60.,       # equator-pole temp gradient (default 60K)
            'delv': 10.,       # lapse rate (default 10K)
            'eps': 0.,         # stratospheric latitudinal variation (default 0K)
            'sigma_b': 0.7,    # boundary layer friction height (default p/ps = sigma = 0.7)
    
            # negative sign is a flag indicating that the units are days
            'ka':   -40.,      # Constant Newtonian cooling timescale (default 40 days)
            'ks':    -4.,      # Boundary layer dependent cooling timescale (default 4 days)
            'kf':   -1.,       # BL momentum frictional timescale (default 1 days)
    
            'do_conserve_energy':   True,  # convert dissipated momentum into heat (default True)
        },
    
        'diag_manager_nml': {
            'mix_snapshot_average_fields': False
        },
    
        'fms_nml': {
            'domains_stack_size': 600000                        # default: 0
        },
    
        'fms_io_nml': {
            'threading_write': 'single',                         # default: multi
            'fileset_write': 'single',                           # default: multi
        }
    })
    exp.namelist = namelist
    exp.set_resolution(resolution_params['horizontal'], resolution_params['vertical'])
    return exp

def simulate(NCORES):
    exp = build_experiment()
    exp.codebase.compile()

    ensemble_params = cfg.get_ensemble_params()

    oneday = 24
    # TODO convert each of the following three stages into a call to a function to configure the next run based on initial file, perturbation, duration 
    # TODO build up a database including graph structure of parents-children 
    # --------- Spinup -------------
    t = 0
    run_label = 0 # for naming the file 
    i_chunk_spu = 0 # for tracking progress along a single segment of the tree 
    while t < ensemble_params['duration_spinup']:
        print(f'>>>>>>>>>>>>{ i_chunk_spu = } <<<<<<<<<<<<<')
        duration_chunk = min(ensemble_params['duration_chunk_max'], ensemble_params['duration_spinup'] - t)
        exp.namelist['main_nml']['days'] = duration_chunk//oneday
        run_label += 1
        exp.run(run_label, num_cores=NCORES, use_restart=False)
        t += duration_chunk
        i_chunk_spu += 1
    run_label_spu = run_label
    # -------- Spinon (ancestor) ---------------
    i_chunk_anc = 0
    while t < ensemble_params['duration_spinup'] + ensemble_params['duration_spinon']:
        print(f'>>>>>>>>>>>>{ i_chunk_anc = } <<<<<<<<<<<<<')
        duration_chunk = min(ensemble_params['duration_chunk_max'], ensemble_params['duration_spinup'] + ensemble_params['duration_spinon'] - t)
        exp.namelist['main_nml']['days'] = duration_chunk//oneday
        run_label += 1
        restart_file = exp.get_restart_file(run_label_spu) if i_chunk_anc==0 else exp.get_restart_file(run_label-1)
        exp.run(run_label, num_cores=NCORES, use_restart=True, restart_file=restart_file)
        t += duration_chunk
        i_chunk_anc += 1
    # -------- Spinoff --------------
    for i_dsc in range(ensemble_params['n_spinoff']):
        print(f'>>>>>>>>>>>>{ i_dsc = } <<<<<<<<<<<<<')
        i_chunk_dsc = 0
        t = ensemble_params['duration_spinup']
        while t < ensemble_params['duration_spinup'] + ensemble_params['duration_spinoff']:
            print(f'>>>>>>>>>>>>{ i_chunk_dsc = } <<<<<<<<<<<<<')
            duration_chunk = min(ensemble_params['duration_chunk_max'], ensemble_params['duration_spinup'] + ensemble_params['duration_spinon'] - t)
            exp.namelist['main_nml']['days'] = duration_chunk//oneday
            run_label += 1
            restart_file = exp.get_restart_file(run_label_spu) if i_chunk_dsc==0 else exp.get_restart_file(run_labl)
            exp.run(run_label, num_cores=NCORES, use_restart=True, restart_file=restart_file)
            t += duration_chunk
            i_chunk_dsc += 1
    return

def main():
    NCORES = 4
    
    todo = dict({
        'simulate':            1,
        })

    if todo['simulate']:
        simulate(NCORES)

#Lets do a run!
if __name__ == '__main__':
    main()
