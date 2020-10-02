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
class MDWorker(rp.task_overlay.Worker):
    '''
    This class provides the required functionality to execute work requests. In
    this simple example, the worker implements the MD simulation (md) command.
    '''

    # --------------------------------------------------------------------------
    def __init__(self, cfg):

        with open('./env.%d' % os.getpid(), 'w') as fout:
            for k in sorted(os.environ.keys()):
                v = os.environ[k]
                fout.write('%s=%s\n' % (k, v))

        rp.task_overlay.Worker.__init__(self, cfg)

        self.register_call('md', self.md)

        self._log.debug('started MD worker %s', self._uid)

    # --------------------------------------------------------------------------
    def pre_exec(self):

        try:
            self._log.debug('pre_exec')
            pass

        except Exception:
            self._log.exception('MD pre_exec failed')
            raise

    # --------------------------------------------------------------------------
    def post_exec(self):

        try:
            self._log.debug('post_exec')
            pass

        except Exception:
            self._log.exception('MD post_exec failed')
            raise

    # --------------------------------------------------------------------------
    def md(self):
        pass


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    md_worker = MDWorker(sys.argv[1])
    md_worker.run()
