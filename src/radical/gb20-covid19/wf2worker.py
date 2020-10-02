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
    def __init__(self, cfg_wl):

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
class AgWorker(rp.task_overlay.Worker):
    '''
    This class provides the required functionality to execute work requests. In
    this simple example, the worker implements the aggregating (ag) command.
    '''

    # --------------------------------------------------------------------------
    def __init__(self, cfg_wl):

        with open('./env.%d' % os.getpid(), 'w') as fout:
            for k in sorted(os.environ.keys()):
                v = os.environ[k]
                fout.write('%s=%s\n' % (k, v))

        rp.task_overlay.Worker.__init__(self, cfg)

        self.register_call('ag', self.ag)

        self._log.debug('started Ag worker %s', self._uid)

    # --------------------------------------------------------------------------
    def pre_exec(self):

        try:
            self._log.debug('pre_exec')
            pass

        except Exception:
            self._log.exception('Ag pre_exec failed')
            raise

    # --------------------------------------------------------------------------
    def post_exec(self):

        try:
            self._log.debug('post_exec')
            pass

        except Exception:
            self._log.exception('Ag post_exec failed')
            raise

    # --------------------------------------------------------------------------
    def ag(self):
        pass


# ------------------------------------------------------------------------------
class MLWorker(rp.task_overlay.Worker):
    '''
    This class provides the required functionality to execute work requests. In
    this simple example, the worker implements the machine learning (ml)
    command.
    '''

    # --------------------------------------------------------------------------
    def __init__(self, cfg_wl):

        with open('./env.%d' % os.getpid(), 'w') as fout:
            for k in sorted(os.environ.keys()):
                v = os.environ[k]
                fout.write('%s=%s\n' % (k, v))

        rp.task_overlay.Worker.__init__(self, cfg)

        self.register_call('ml', self.ml)

        self._log.debug('started ML worker %s', self._uid)

    # --------------------------------------------------------------------------
    def pre_exec(self):

        try:
            self._log.debug('pre_exec')
            pass

        except Exception:
            self._log.exception('ML pre_exec failed')
            raise

    # --------------------------------------------------------------------------
    def post_exec(self):

        try:
            self._log.debug('post_exec')
            pass

        except Exception:
            self._log.exception('ML post_exec failed')
            raise

    # --------------------------------------------------------------------------
    def ml(self):
        pass


# ------------------------------------------------------------------------------
class OdWorker(rp.task_overlay.Worker):
    '''
    This class provides the required functionality to execute work requests. In
    this simple example, the worker implements the outlier detection (od)
    command.
    '''

    # --------------------------------------------------------------------------
    def __init__(self, cfg_wl):

        with open('./env.%d' % os.getpid(), 'w') as fout:
            for k in sorted(os.environ.keys()):
                v = os.environ[k]
                fout.write('%s=%s\n' % (k, v))

        rp.task_overlay.Worker.__init__(self, cfg)

        self.register_call('od', self.od)

        self._log.debug('started Od worker %s', self._uid)

    # --------------------------------------------------------------------------
    def pre_exec(self):

        try:
            self._log.debug('pre_exec')
            pass

        except Exception:
            self._log.exception('Od pre_exec failed')
            raise

    # --------------------------------------------------------------------------
    def post_exec(self):

        try:
            self._log.debug('post_exec')
            pass

        except Exception:
            self._log.exception('Od post_exec failed')
            raise

    # --------------------------------------------------------------------------
    def md(self):
        pass


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    cfg_file = sys.argv[1]
    cfg_wl = ru.Config(cfg=ru.read_json(cfg_file))

    md_worker = MDWorker(sys.argv[1], cfg_wl)
    ag_worker = MDWorker(sys.argv[1], cfg_wl)
    ml_worker = MDWorker(sys.argv[1], cfg_wl)
    od_worker = MDWorker(sys.argv[1], cfg_wl)

    for iter in range(0, cfg_wl['MAX_STAGE']):
        md_worker.run()
        ag_worker.run()
        ml_worker.run()
        od_worker.run()