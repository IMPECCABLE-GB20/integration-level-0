#!/usr/bin/env python3

from radical.entk import Pipeline, Stage, Task

def generate_ml1_pipeline(cfg):

    # configs

    # setup EnTK pipeline
    p = Pipeline()
    p.name = 'ML1'
    s = Stage()
    t = Task()

    # ML task
    t.pre_exec = [
        'module reset',
        'module load gcc/7.4.0',
        'module load python/3.6.6-anaconda3-5.3.0',
        'module load cuda/10.1.243',
        'module load hdf5/1.10.4',
        'export LC_ALL=en_US.utf-8',
        'export LANG=en_US.utf-8',
        'source activate %s' % cfg['ml1_conda_env'],
        'export device=${OMPI_COMM_WORLD_LOCAL_RANK:=0}',
        # 'export data_root=%s' % cfg['data_root'],
        'cd %s' % cfg['base_path']
        ]

    t.executable = ['%s/python' % cfg['python_bin_path']]
    t.arguments = [
        '-u'  , 'infer_images.py',
        '-t'  , '0',
        '-d'  , '${device}',
        '-i'  , '"%s/images_compressed/*.pkl.gz"' % cfg['data_root'],
        '-o'  , '/gpfs/alpine/proj-shared/med110/cov19_data/scores',
        '-m'  , '/gpfs/alpine/proj-shared/med110/tkurth/attention_meta/v2/model_6W02.pt',
        '-trt', '/gpfs/alpine/proj-shared/med110/tkurth/attention_meta/v2/model_6W02.trt',
        '--stage_dir', '/mnt/bb/%s' % cfg['userid'],
        '--num_stage_workers', '4',
        '--output_frequency', '200',
        '--update_frequency', '10',
        '-b', '256',
        '-j', '4',
        '-dtype=fp16',
        '-num_calibration_batches=10',
        '--distributed'
        ]

    t.gpu_reqs = {
        'processes'          : 120,
        'threads_per_process': 1,
        'thread_type'        : None,
        'process_type'       : "MPI"
        }

    s.add_tasks(t)
    p.add_stages(s)

    return p
