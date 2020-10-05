#!/usr/bin/env python3

import os
import sys
import glob
import time
import json

import radical.utils as ru
import radical.pilot as rp

# ------------------------------------------------------------------------------
class MDMaster(rp.task_overlay.Master):
    '''
    This class provides the communication setup for the task overlay: it will
    set up the request / response communication queus and provide the endpoint
    information to be forwarded to the workers.
    '''

    # --------------------------------------------------------------------------
    def __init__(self, cfg):

        # initialized the task overlay base class.  That base class will ensure
        # proper communication channels to the pilot agent.
        rp.task_overlay.Master.__init__(self, cfg=cfg)

        print('%s: cfg from %s to %s' % (self._uid, cfg.idx, cfg.n_masters))

        self.parse_csv()

    # --------------------------------------------------------------------------
    def create_work_items(self):

        self._prof.prof('create_start')

        name = self._cfg.workload.name

        # create an initial list of work items to be distributed to the workers.
        # Work items MUST be serializable dictionaries.
        for i in range(0, cfg['MAX_STAGE']):
            uid  = '%s.request.%06d' % (name, i)

            print('=== uid:', uid)

            item = {'uid'  :   uid,
                    'mode' :  'exec', # popen call for a executable task
                    'cores': 1,
                    'gpus' : 1,
                    'data' : {
                        'exe' : '%s/bin/python' % cfg['conda_openmm'],
                        'args': ['%s/MD_exps/%s/run_openmm.py' % (cfg['base_path'], cfg['system_name'])],
                        # for exports
                        'env' : {
                            'PYTHONPATH': '%s/MD_exps:%s/MD_exps/MD_utils:$PYTHONPATH' %
                                (cfg['base_path'], cfg['base_path']),

                                       }}}
            self.request(item)

        self._prof.prof('create_stop')



# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # This master script runs as a task within a pilot allocation.  The purpose
    # of this master is to (a) spawn a set or workers within the same
    # allocation, (b) to distribute work items (`dock` function calls) to those
    # workers, and (c) to collect the responses again.
    cfg_fname    = 'wf2_md.cfg'
    cfg          = ru.Config(cfg=ru.read_json(cfg_fname))
    cfg.idx      = int(sys.argv[1])

    # FIXME: worker startup should be moved into master
    workload   = cfg.workload
    n_nodes    = cfg.nodes
    cpn        = cfg.cpn
    gpn        = cfg.gpn

    # Prepare dirlist in case we are iterating and we have detected outliers
    initial_MD = True
    outlier_filepath = '%s/Outlier_search/restart_points.json' % cfg['base_path']

    if os.path.exists(outlier_filepath):
        initial_MD = False
        outlier_file = open(outlier_filepath, 'r')
        outlier_list = json.load(outlier_file)
        outlier_file.close()

    # NOTE: pre-exec can go here as in wf0 cfg to load the python environment
    # for HOMOGENEOUS task.
    time_stamp = int(time.time())
    cfg.worker_descr['pre_exec'].append(
        'conda activate %s' % cfg['conda_openmm'])
    cfg.worker_descr['pre_exec'].append(
        'cd %s/MD_exps/%s' % (cfg['base_path'], cfg['system_name']))
    cfg.worker_descr['pre_exec'].append(
        'mkdir -p omm_runs_%d && cd omm_runs_%d' % (time_stamp+i, time_stamp+i))

    descr      = cfg.worker_descr

    # one node is used by master.  Alternatively (and probably better), we could
    # reduce one of the worker sizes by one core.  But it somewhat depends on
    # the worker type and application workload to judge if that makes sense, so
    # we leave it for now.
    n_workers = cfg.n_workers
    print('n_workers', n_workers)

    # create a master class instance - this will establish communitation to the
    # pilot agent
    master = MDMaster(cfg)

    # insert `n` worker tasks into the agent.  The agent will schedule (place)
    # those workers and execute them.  Insert one smaller worker (see above)
    # NOTE: this assumes a certain worker size / layout
    print('cpn: %d' % cpn)
    print('gpn: %d' % gpn)
    master.submit(descr=descr, count=n_workers, cores=cpn,     gpus=gpn)
  # master.submit(descr=descr, count=1,         cores=cpn - 1, gpus=gpn)

    # wait until `m` of those workers are up
    # This is optional, work requests can be submitted before and will wait in
    # a work queue.
  # master.wait(count=nworkers)

    master.run()

    # simply terminate
    # FIXME: clean up workers

    # collect sdf files
    # os.system('sh -c "cat out.worker.*.sdf | gzip > %s.sdf.gz"' % workload.name)