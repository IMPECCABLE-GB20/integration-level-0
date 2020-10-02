#!/usr/bin/env python3

import os
import sys
import glob
import time
import shutil

import multiprocessing as mp
import radical.pilot as rp
import radical.utils as ru

# ------------------------------------------------------------------------------
#
class MyWorker(rp.task_overlay.Worker):
    '''
    This class provides the required functionality to execute work requests. In
    this simple example, the worker implements a pipeline of 4 workloads: 1. MD
    simulation (md); 2. aggregation (ag); 3. machine learning (ml); 4. outlier
    identification (od). The pipeline is repeated a configurable number of
    times.
    '''

    # --------------------------------------------------------------------------
    def __init__(self, cfg):

        with open('./env.%d' % os.getpid(), 'w') as fout:
            for k in sorted(os.environ.keys()):
                v = os.environ[k]
                fout.write('%s=%s\n' % (k, v))

        rp.task_overlay.Worker.__init__(self, cfg)

        self.register_call('md', self.md)
        self.register_call('ag', self.ag)
        self.register_call('ml', self.ml)
        self.register_call('od', self.od)

        self._log.debug('started worker %s', self._uid)

    # --------------------------------------------------------------------------
    def pre_exec(self):

        try:
            self._log.debug('pre_exec')
            pass

        except Exception:
            self._log.exception('pre_exec failed')
            raise

    # --------------------------------------------------------------------------
    def post_exec(self):

        try:
            self._log.debug('post_exec')
            pass

        except Exception:
            self._log.exception('post_exec failed')
            raise

    # --------------------------------------------------------------------------
    def md():
        pass

    # --------------------------------------------------------------------------
    def ag():
        pass

    # --------------------------------------------------------------------------
    def ml():
        pass

    # --------------------------------------------------------------------------
    def od():
        pass


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # the `info` dict is passed to the worker as config file.
    # Create the worker class and run it's work loop.
    worker = MyWorker(sys.argv[1])
    worker.run()