#!/usr/bin/env python3

import os
import sys
import glob
import pprint

import radical.utils as ru
import radical.saga  as rs
import radical.pilot as rp

from radical.entk import Pipeline, Stage, Task


global p_map
p_map = dict()  # pilot: [task, task, ...]


# ------------------------------------------------------------------------------
def check_runs(cfg_file, run_file):

    runs      = list()
    n_smiles  = dict()

    rec_path  = 'input/receptors.ad/'    # FIXME
    smi_path  = 'input/smiles/'          # FIXME

    cfg       = ru.Config(cfg=ru.read_json(cfg_file))
    res_path  = cfg.fs_url + cfg.workload.results

    fs        = rs.filesystem.Directory(res_path)

    with open(run_file, 'r') as fin:

        for line in fin.readlines():

            line  = line.strip()

            if not line:
                continue

            if line.startswith('#'):
                continue

            elems = line.split()

            assert(len(elems) == 4), line

            receptor  = str(elems[0])
            smiles    = str(elems[1])
            n_workers = int(elems[2])
            runtime   = int(elems[3])

            runs.append([receptor, smiles, n_workers, runtime])

    return runs

# ----------------------------------------------------------------------------
def generate_pipeline(cfg):

    cfg_file  = cfg['run_cfg_file']  # resource and workload config
    run_file  = cfg['run_file']      # runs for this campaign

    # setup S1 workload
    cfg     = ru.Config(cfg=ru.read_json(cfg_file))
    runs    = check_runs(cfg_file, run_file)

    if not runs:
        print('S1: nothing to run, exiting.')
        return

    # for each run in the campaign:
    # - create cfg with requested receptor and smiles
    # - create a number of masters as EnTK tasks and add them to a pipeline
    # - submit configured number of masters with that cfg

    # setup EnTK pipeline
    p = Pipeline()
    p.name = 'S1.RAPTOR'
    s = Stage()

    # create cfg
    subs = dict()
    rurl = cfg.fs_url + cfg.workload.results
    d    = rs.filesystem.Directory(rurl)
    ls   = [str(u).split('/')[-1] for u in d.list()]

    workload  = cfg.workload

    for receptor, smiles, n_workers, runtime in runs:

        print('%30s  %s'   % (receptor, smiles))
        name = '%s_-_%s'   % (receptor, smiles)
        tgt  = '%s.%s.gz'  % (name, workload.output)

        cpw       = cfg.cpw
        gpw       = cfg.gpw
        n_masters = cfg.n_masters

        cfg.workload.receptor = receptor
        cfg.workload.smiles   = smiles
        cfg.workload.name     = name
        cfg.runtime           = runtime
        cfg.n_workers         = n_workers
        print('n_workers: %d'  % cfg.n_workers)

        ru.write_json(cfg, 'configs/wf0.%s.cfg' % name)

        for i in range(n_masters):
            t = Task()

            t.pre_exec = [
                '. /gpfs/alpine/scratch/mturilli1/med110/radical.pilot.sandbox/s1.to/bin/activate'
            ]

            t.executable           = "python3"
            t.arguments            = ['wf0_master.py', i]
            t.cpu_reqs             = {'processes'          : 1,
                                      'threads_per_process': 4,
                                      'thread_type'        : None,
                                      'process_type'       : None}
            t.upload_input_data    = ['wf0_master.py',
                                      'wf0_worker.py',
                                      'configs/wf0.%s.cfg > wf0.cfg' % name,
                                      'read_ligand_dict.py']
            t.link_input_data      = ['%s > input_dir' % workload.input_dir]
            #t.download_output_data = ['%s.%s.gz > results/%s.%s.gz' %
            #    (name, workload.output, name, workload.output)]

            s.add_tasks(t)

    p.add_stages(s)

    return p

