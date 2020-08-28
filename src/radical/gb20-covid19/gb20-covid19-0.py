#!/usr/bin/env python3

import os
import sys

import radical.utils as ru
import radical.pilot as rp
import radical.entk as entk

import wf2
import wf3

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
def wf2(appman):
    p1 = wf2.generate_training_pipeline()
    pipelines = [p1]
    appman.workflow = pipelines
    appman.run()

# ------------------------------------------------------------------------------
def wf3(appman):
    esmacs_ties = wf3.EsmacsTies(appman)
    esmacs_ties.wf3()
    esmacs_ties.run()


# ==============================================================================
if __name__ == '__main__':

    reporter = ru.Reporter(name='radical.entk')
    reporter.title('GB20 COVID-19')

    # resource specified as argument
    if len(sys.argv) == 3:
        cfg_file = sys.argv[1]
        cfg_wf2_file = sys.argv[2]
        cfg_wf3_file = sys.argv[3]
    else:
        reporter.exit('Usage:\t%s [config.json] [config_wf2.json] [config_wf3.json]\n\n' % sys.argv[0])

    try:
        cfg = ru.Config(cfg=ru.read_json(cfg_file))
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
            if wf == 'wf2':
                wf2(appman)
            elif wf == 'wf3':
                wf3(appman)
            else:
                raise Exception("ERROR: unrecognized workflow %s" % wf)

        appman.terminate()


    except Exception as e:
        print('Error: ', e)
        raise