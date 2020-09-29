#!/usr/bin/env python3

import os
import sys

import radical.utils as ru
import radical.pilot as rp
import radical.entk as entk

import wf1 as wf1
import wf2 as wf2
import wf3 as wf3


# ------------------------------------------------------------------------------
def check_environment():
    return True

# ------------------------------------------------------------------------------
def get_pilot_description(pdesc):
    ret = {
        'resource': pdesc['resource'],
        'queue'   : pdesc['queue'],
        'schema'  : pdesc['schema'],
        'walltime': pdesc['walltime'],
        'cpus'    : pdesc['cpus_node'] * 4 * pdesc['nodes'],
        'gpus'    : 6 * pdesc['nodes'],
        'project' : pdesc['project']
    }
    return ret

# ------------------------------------------------------------------------------
def ml1_run(appman, cfg, reporter):
    reporter.header('Executing ML1')
    pass

# ------------------------------------------------------------------------------
def wf1_run(appman, cfg, reporter, counter=1):
    print(cfg)
    p1 = wf1.generate_pipeline(cfg)
    appman.workflow = [p1]

    reporter.header('Executing S1')
    appman.run()

# ------------------------------------------------------------------------------
def wf3_run_cg(appman, cfg, reporter, counter=1):
    pipelines = []

    # Creates the requested number of concurrent pipelines
    for i in range(0,counter):
        pipelines.append(wf3.generate_esmacs(cfg))

    appman.workflow = pipelines

    reporter.header('Executing S3')
    appman.run()

# ------------------------------------------------------------------------------
def wf2_run(appman, cfg, reporter, counter=1):
    cfg['node_counts'] = cfg['md_counts'] // cfg['gpu_per_node']
    p1 = wf2.generate_training_pipeline(cfg)
    appman.workflow = [p1]

    reporter.header('Executing S2')
    appman.run()

# ------------------------------------------------------------------------------
def get_wf3_input(appman, cfg):
    # Assuming shared filesystem on login node this can be executed by the
    # script instead of EnTK.
    p = entk.Pipeline()
    p.name = 'get_wf3_input'
    s = entk.Stage()

    t = entk.Task()
    t.executable = ['python3']
    t.arguments = ['gather.py', '-f', cfg['outlier_path'], '-p', cfg['top_path']]

    s.add_tasks(t)
    p.add_stages(s)
    appman.workflow = [p]

    appman.run()

# ------------------------------------------------------------------------------
def wf3_run_fg(appman, cfg, reporter, counter=1):
    pipelines = []

    # Creates the requested number of concurrent pipelines
    for i in range(0,counter):
        pipelines.append(wf3.generate_esmacs(cfg))

    appman.workflow = pipelines

    reporter.header('Executing S3')
    appman.run()


# ==============================================================================
if __name__ == '__main__':

    reporter = ru.Reporter(name='radical.entk')
    reporter.title('GB20 COVID-19')

    # resource specified as argument
    if len(sys.argv) == 5:
        cfg_file = sys.argv[1]
        cfg_wf1_file = sys.argv[2]
        cfg_wf2_file = sys.argv[3]
        cfg_wf3_file = sys.argv[4]
    else:
        reporter.exit('Usage:\t%s [config.json] [config_wf1.json] [config_wf2.json] [config_wf3.json]\n\n' % sys.argv[0])

    try:
        cfg = ru.Config(cfg=ru.read_json(cfg_file))
        cfg_wf1 = ru.Config(cfg=ru.read_json(cfg_wf1_file))
        cfg_wf2 = ru.Config(cfg=ru.read_json(cfg_wf2_file))
        cfg_wf3 = ru.Config(cfg=ru.read_json(cfg_wf3_file))

        if not check_environment():
            raise("ERROR: Incorrect environment set up.")

        pdesc = get_pilot_description(cfg['pdesc'])

        appman = entk.AppManager(
            hostname=os.environ.get('RMQ_HOSTNAME'),
            port=int(os.environ.get('RMQ_PORT')),
            username=os.environ.get('RMQ_USERNAME'),
            password=os.environ.get('RMQ_PASSWORD'),
            autoterminate=False)
        appman.resource_desc = pdesc

        for wf in cfg['workflows']:
            if wf == 'ml1':
                reporter.header('Submit ML1')
                ml1_run(appman, cfg_ml1, reporter)
                reporter.header('ML1 done')

            elif wf == 'wf1':
                reporter.header('Submit S1')
                wf1_run(appman, cfg_wf1, reporter)
                reporter.header('S1 done')

            elif wf == 'wf3cg':
                reporter.header('Submit S3')
                # get_wf3_input(appman, cfg_wf3)
                counter = 10
                wf3_run_cg(appman, cfg_wf3, reporter, counter)
                reporter.header('S3 done')

            elif wf == 'wf2':
                reporter.header('Submit S2')
                wf2_run(appman, cfg_wf2, reporter)
                reporter.header('S2 done')

            elif wf == 'wf3fg':
                reporter.header('Submit S3')
                # get_wf3_input(appman, cfg_wf3)
                counter = 10
                wf3_run_fg(appman, cfg_wf3, reporter, counter)
                reporter.header('S3 done')

            else:
                raise Exception("ERROR: unrecognized workflow %s" % wf)

        appman.terminate()


    except Exception as e:
        appman.terminate()
        print('Error: ', e)
        raise
