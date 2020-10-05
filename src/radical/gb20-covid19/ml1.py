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
    t.pre_exec = ['. /gpfs/alpine/scratch/mturilli1/med110/radical.pilot.sandbox/s1.to/bin/activate']

    t.executable = "run_infer.sh"
    t.gpu_reqs   = {'processes'          : 120,
                    'threads_per_process': 1,
                    'thread_type'        : None,
                    'process_type'       : "MPI"}

    s.add_tasks(t)
    p.add_stages(s)

    return p
