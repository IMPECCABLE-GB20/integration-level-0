#!/usr/bin/env python3

import os
import sys

import radical.utils as ru


# ------------------------------------------------------------------------------
def get_configs(cfg):
    cfg = ru.Config(cfg=ru.read_json(cfg_file))

    for wf in cfg.keys():
        assert cfg[wf]["cmd"],"ERROR: %s: Undefined command." % wf

    return cfg

# ------------------------------------------------------------------------------
def run_workflow(wf):

    cmd = wf["cmd"]+' '

    if wf["args"]:
        cmd += ' '.join(wf["args"])

    os.system(cmd)


# ==============================================================================
if __name__ == '__main__':

    cfg_file  = sys.argv[1]  # workflows configs

    try:
        cfg = get_configs(cfg_file)

        for wf in cfg.keys():
            run_workflow(cfg[wf])

    except Exception as e:
        print('Error: ', e)
        raise

