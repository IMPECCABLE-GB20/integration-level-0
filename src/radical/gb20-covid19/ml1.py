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
        '. %s/bin/activate' % cfg['penv'],
        'export device=${OMPI_COMM_WORLD_LOCAL_RANK:=0}',
        'export data_root="/gpfs/alpine/med110/world-shared/ULT911"']

    t.executable = ['%s/bin/python' % (cfg['conda_pytorch'])]  # MD_to_CVAE.py
    t.arguments = [
            '-u'  , 'infer_images.py',
            '-t'  , '0',
            '-d'  , '${device}',
            '-i'  , '"${data_root}/images_compressed/*.pkl.gz"',
            '-o'  , '/gpfs/alpine/proj-shared/med110/cov19_data/scores',
            '-m'  , '/gpfs/alpine/proj-shared/med110/tkurth/attention_meta/v2/model_6W02.pt',
            '-trt', '/gpfs/alpine/proj-shared/med110/tkurth/attention_meta/v2/model_6W02.trt',
            '--stage_dir', '/mnt/bb/${USER}',
            '--num_stage_workers', '4',
            '--output_frequency', '200',
            '--update_frequency', '10',
            '-b', '256',
            '-j', '4',
            '-dtype=fp16',
            '-num_calibration_batches=10',
            '--distributed']
    t.gpu_reqs = {'processes'          : 120,
                  'threads_per_process': 1,
                  'thread_type'        : None,
                  'process_type'       : "MPI"}

    s.add_tasks(t)
    p.add_stages(s)

    return p
