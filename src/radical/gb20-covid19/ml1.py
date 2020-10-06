#!/usr/bin/env python3

from radical.entk import Pipeline, Stage, Task

def generate_ml1_pipeline(cfg):

    # configs

    # setup EnTK pipeline
    p = Pipeline()
    p.name = 'ML1'
    s = Stage()
    t = Task()

    # Native RCT
    # ML task
    # t.pre_exec = [
    #     '. /sw/summit/lmod/lmod/init/profile',
    #     'module load gcc/7.4.0',
    #     'module load python/3.6.6-anaconda3-5.3.0',
    #     'module load cuda/10.1.243',
    #     'module load hdf5/1.10.4',
    #     'export LC_ALL=en_US.utf-8',
    #     'export LANG=en_US.utf-8',
    #     'source activate %s' % cfg['ml1_conda_env'],
    #     'export device=${OMPI_COMM_WORLD_LOCAL_RANK:=0}',
    #     'export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:%s' % cfg['ld_lib_path'],
    #     # 'export data_root=%s' % cfg['data_root'],
    #     'cd %s' % cfg['base_path']
    #     ]
    # t.executable = ['%s/python' % cfg['python_bin_path']]
    # t.arguments = [
    #     '-u'  , 'infer_images.py',
    #     '-t'  , '0',
    #     '-d'  , '${device}',
    #     '-i'  , '"%s/images_compressed/*.pkl.gz"' % cfg['data_root'],
    #     '-o'  , cfg['output_dir'],
    #     '-m'  , cfg['model'],
    #     '-trt', cfg['trt'],
    #     '--stage_dir', '/mnt/bb/%s' % cfg['userid'],
    #     '--num_stage_workers', '4',
    #     '--output_frequency', '200',
    #     '--update_frequency', '10',
    #     '-b', '256',
    #     '-j', '4',
    #     '-dtype=fp16',
    #     '-num_calibration_batches=10',
    #     '--distributed'
    #     ]

    # Bash wrapper
    t.executable = ['%s/ml1.sh' % cfg['exec_path']]
    t.arguments = ['--distributed', cfg['ld_lib_path'], cfg['data_root'],
                   cfg['base_path'], cfg['ml1_conda_env'], cfg['output_dir'],
                   cfg['model'], cfg['trt'], cfg['userid']]

    t.cpu_reqs = {
        'processes'          : cfg['processes'],
        'threads_per_process': 4,
        'thread_type'        : 'OpenMP',
        'process_type'       : 'MPI'
        }
    t.gpu_reqs = {
        'processes'          : 1,
        'threads_per_process': 1,
        'thread_type'        : 'CUDA',
        'process_type'       : 'MPI'
        }

    s.add_tasks(t)
    p.add_stages(s)

    return p
