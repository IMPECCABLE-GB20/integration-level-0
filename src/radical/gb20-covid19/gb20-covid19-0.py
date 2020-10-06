#!/usr/bin/env python3

import os
import sys

import radical.utils as ru
import radical.pilot as rp
import radical.entk as entk

import ml1 as ml1
import wf1 as wf1
import wf2 as wf2
import wf3 as wf3


# ------------------------------------------------------------------------------
def check_environment():
    return True

# ------------------------------------------------------------------------------
def ml1_run(appman, cfg, reporter):
    p1 = ml1.generate_ml1_pipeline(cfg)
    appman.workflow = [p1]

    reporter.header('Executing ML1')
    appman.run()

# ------------------------------------------------------------------------------
def wf1_run(appman, cfg, reporter, counter=1):
    print(cfg)
    p1 = wf1.generate_pipeline(cfg)
    appman.workflow = [p1]

    reporter.header('Executing S1')
    appman.run()

# ------------------------------------------------------------------------------
def wf2_run(appman, cfg, reporter, counter=1):
    cfg['node_counts'] = cfg['md_counts'] // cfg['gpu_per_node']
    pipelines = []

    # Creates the requested number of concurrent pipelines
    for i in range(0,counter):
        pipelines.append(wf2.generate_training_pipeline(cfg))

    appman.workflow = pipelines

    reporter.header('Executing S2')
    appman.run()

# ------------------------------------------------------------------------------
def get_wf3_input(appman, cfg):
    pass

# ------------------------------------------------------------------------------
def wf3_run(appman, cfg, reporter, counter=1):
    pipelines = []

    # Creates the requested number of concurrent pipelines
    for i in range(0,counter):
        pipelines.append(wf3.generate_esmacs(cfg))

    appman.workflow = pipelines

    reporter.header('Executing S3%s' % cfg['type_esmacs'])
    appman.run()


# ==============================================================================
if __name__ == '__main__':

    reporter = ru.Reporter(name='radical.entk')
    reporter.title('GB20 COVID-19')

    # resource specified as argument
    if len(sys.argv) == 7:
        cfg_file = sys.argv[1]
        cfg_ml1_file = sys.argv[2]
        cfg_wf1_file = sys.argv[3]
        cfg_wf2_file = sys.argv[4]
        cfg_wf3_cg_file = sys.argv[5]
        cfg_wf3_fg_file = sys.argv[6]

    else:
        reporter.exit('Usage:\t%s [config.json] [config_ml1.json] [config_wf1.json] [config_wf2.json] [config_wf3_cg.json] [config_wf3_fg.json]\n\n' % sys.argv[0])

    try:
        cfg = ru.Config(cfg=ru.read_json(cfg_file))
        cfg_ml1 = ru.Config(cfg=ru.read_json(cfg_ml1_file))
        cfg_wf1 = ru.Config(cfg=ru.read_json(cfg_wf1_file))
        cfg_wf2 = ru.Config(cfg=ru.read_json(cfg_wf2_file))
        cfg_wf3_cg = ru.Config(cfg=ru.read_json(cfg_wf3_cg_file))
        cfg_wf3_fg = ru.Config(cfg=ru.read_json(cfg_wf3_fg_file))

        if not check_environment():
            raise("ERROR: Incorrect environment set up.")

        pdesc = {
            'resource': cfg['pdesc']['resource'],
            'queue'   : cfg['pdesc']['queue'],
            'schema'  : cfg['pdesc']['schema'],
            'walltime': cfg['pdesc']['walltime'],
            'cpus'    : cfg['pdesc']['cpus_node'] * 4 * cfg['pdesc']['nodes'],
            'gpus'    : 6 * cfg['pdesc']['nodes'],
            'project' : cfg['pdesc']['project']
        }

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
                counter = 40
                wf3_run(appman, cfg_wf3_cg, reporter, counter)
                reporter.header('S3cg done')

            elif wf == 'wf2':
                reporter.header('Submit S2')
                counter = 2
                wf2_run(appman, cfg_wf2, reporter)
                reporter.header('S2 done')

            elif wf == 'wf3fg':
                reporter.header('Submit S3')
                # get_wf3_input(appman, cfg_wf3)
                counter = 10
                wf3_run(appman, cfg_wf3_fg, reporter, counter)
                reporter.header('S3fg done')

            else:
                raise Exception("ERROR: unrecognized workflow %s" % wf)

        appman.terminate()


    except Exception as e:
        appman.terminate()
        print('Error: ', e)
        raise
