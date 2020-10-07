#!/usr/bin/env python

import os
import sys

import radical.pilot as rp
import radical.utils as ru

# ------------------------------------------------------------------------------
if __name__ == '__main__':

    report = ru.Reporter(name='radical.pilot')
    report.title('S3 for multi dvm')

    if len(sys.argv) == 2:
        cfg_file = sys.argv[1]

    session = rp.Session()

    try:

        cfg = ru.Config(cfg=ru.read_json(cfg_file))

        pd_init = {
            'resource'     : cfg['pdesc']['resource'],
            'exit_on_error': True,
            'project'      : cfg['pdesc']['project'],
            'queue'        : cfg['pdesc']['queue'],
            'access_schema': cfg['pdesc']['schema'],
            'runtime'      : cfg['pdesc']['runtime'],
            'cores'        : cfg['pdesc']['cpus_node'] * 4 * cfg['pdesc']['nodes'],
            'gpus'         : 6 * cfg['pdesc']['nodes']
        }

        report.header('submit pilots')
        pmgr   = rp.PilotManager(session=session)
        umgr   = rp.UnitManager(session=session)
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr.add_pilots(pilot)

        n_tasks = 1024
        report.header('submit %d units' % n_tasks)
        report.progress_tgt(n_tasks, label='create')

        cuds = list()

        for i in range(0, n_tasks):
            cud = rp.ComputeUnitDescription()

            cud.executable = '%s/wf3.sh' % cfg['lig_dir']
            cud.args = [cfg['lig_dir'], 1, 'outdir', 'stage',
                        cfg['conda_init'],
                        cfg['conda_esmacs_task_env'],
                        cfg['esmacs_task_modules']]

            cud.cpu_processes   = 1
            cud.cpu_threads     = 4
            cud.cpu_thread_type = 'OpenMP'
            cud.gpu_processes   = 1
            cud.gpu_thread_type = 'CUDA'
            cuds.append(cud)
            report.progress()

        report.progress_done()

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        umgr.submit_units(cuds)

        # Wait for all compute units to reach a final state (DONE, CANCELED or FAILED).
        umgr.wait_units()


    except Exception as e:
        # Something unexpected happened in the pilot code above
        report.error('caught Exception: %s\n' % e)
        ru.print_exception_trace()
        raise

    except (KeyboardInterrupt, SystemExit):
        # the callback called sys.exit(), and we can here catch the
        # corresponding KeyboardInterrupt exception for shutdown.  We also catch
        # SystemExit (which gets raised if the main threads exits for some other
        # reason).
        ru.print_exception_trace()
        report.warn('exit requested\n')

    finally:
        # always clean up the session, no matter if we caught an exception or
        # not.  This will kill all remaining pilots.
        report.header('finalize')
        session.close(download=True)

    report.header()