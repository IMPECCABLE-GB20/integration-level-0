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
#
# def unit_state_cb(unit, state):

#     # terminate pilots once all masters running it are completed,

#     global p_map

#     if state not in rp.FINAL:
#         return True

#     print('unit state: %s -> %s' % (unit.uid, state))
#     pilot = None
#     for p in p_map:
#         for u in p_map[p]:
#             if u.uid == unit.uid:
#                 pilot = p
#                 break
#         if pilot:
#             break

#     # every master should be associated with one pilot
#     assert(pilot), [pilot.uid, unit.uid, pprint.pformat(pilot.as_dict())]

#     to_cancel = True
#     for u in p_map[pilot]:
#         if u.state not in rp.FINAL:
#             to_cancel = False
#             break

#     if to_cancel:
#         print('cancel pilot %s' % pilot.uid)
#         pilot.cancel()
#     else:
#         print('pilot remains active: %s' % pilot.uid)

#     return True


# ------------------------------------------------------------------------------
#
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

            receptor = str(elems[0])
            smiles   = str(elems[1])
            nodes    = int(elems[2])
            runtime  = int(elems[3])

            runs.append([receptor, smiles, nodes, runtime])

        #     assert(receptor)
        #     assert(smiles)
        #     assert(nodes)
        #     assert(runtime)

        #   # print('%s/%s.pdbqt' % (rec_path, receptor))
        #   # print('%s/%s.csv'   % (smi_path, smiles))
        #     assert(os.path.isfile('%s/%s.pdbqt' % (rec_path, receptor)))
        #     assert(os.path.isfile('%s/%s.csv'   % (smi_path, smiles)))

        #     fname = '%s_-_%s.idx' % (receptor, smiles)
        #     pname = '%s/%s'       % (smiles,   fname)
        #     lname = '/tmp/%s'     % (fname)

        #     if not fs.is_file(pname):
        #         n_have = 0
        #     else:
        #         ret = fs.list(pname)
        #         fs.copy(pname, 'file://localhost/%s' % lname)
        #         out, err, ret = ru.sh_callout('wc -l %s | cut -f 1 -d " "' % lname,
        #                                       shell=True)
        #         n_have = int(out)


        #     if smiles in n_smiles:
        #         n_need = n_smiles[smiles]

        #     else:
        #         sname = '%s/%s.csv' % (smi_path, smiles)
        #         out, err, ret = ru.sh_callout('wc -l %s | cut -f 1 -d " "' % sname,
        #                                       shell=True)
        #         n_need = int(out) - 1
        #         n_smiles[smiles] = n_need

        #     if n_need > n_have:
        #         perc = int(100 * n_have / n_need)
        #         print('run  %-30s %-25s [%3d%%]' % (receptor, smiles, perc))
        #         runs.append([receptor, smiles, nodes, runtime])
        #     else:
        #         print('skip %-30s %-25s [100%%]' % (receptor, smiles))

    return runs


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
    p.name = 'S1-RAPTOR'
    s = Stage()

    # create cfg
    subs = dict()
    rurl = cfg.fs_url + cfg.workload.results
    d    = rs.filesystem.Directory(rurl)
    ls   = [str(u).split('/')[-1] for u in d.list()]

    workload  = cfg.workload

    for receptor, smiles, nodes, runtime in runs:

        print('%30s  %s'   % (receptor, smiles))
        name = '%s_-_%s'   % (receptor, smiles)
        tgt  = '%s.%s.gz'  % (name, workload.output)
        # rec  = False

        # if tgt in ls:
        #     if workload.recompute:
        #         rec += 1
        #         d.move(tgt, tgt + '.bak')
        #     else:
        #         print('skip      1 %s' % name)
        #         continue

        # if smiles in ls:
        #     if smiles not in subs:
        #         subs[smiles] = [str(u).split('/')[-1]  for u in d.list('%s/*' % smiles)]
        #     if tgt in subs[smiles]:
        #         if workload.recompute:
        #             rec += 2
        #             d.move('%s/%s'     % (smiles, tgt),
        #                     '%s/%s.bak' % (smiles, tgt))
        #         else:
        #             print('skip      2 %s' % name)
        #             continue

        ## if os.path.exists('results/%s.%s.gz' % (name, wofkload.output)):
        ##     print('skip      3 %s' % name)
        ##     continue

        #if rec: print('recompute %d %s' % (rec, name))
        #else  : print('compute   2 %s'  %       name)

        cpn       = cfg.cpn
        gpn       = cfg.gpn
        n_masters = cfg.n_masters

        cfg.workload.receptor = receptor
        cfg.workload.smiles   = smiles
        cfg.workload.name     = name
        cfg.nodes             = nodes
        cfg.runtime           = runtime
        cfg.n_workers         = int(nodes / n_masters - 1)
        print('n_workers: %d'  % cfg.n_workers)

        ru.write_json(cfg, 'configs/wf0.%s.cfg' % name)

        for i in range(n_masters):
            t = Task()

            t.pre_exec = ['. /gpfs/alpine/scratch/mturilli1/med110/radical.pilot.sandbox/s1.to/bin/activate']

            t.executable           = "python3"
            t.arguments            = ['wf0_master.py', i]
            t.cpu_threads          = cpn
            t.upload_input_data    = ['wf0_master.py',
                                      'wf0_worker.py',
                                      'configs/wf0.%s.cfg > wf0.cfg' % name,
                                      'read_ligand_dict.py']
            t.link_input_data      = ['%s > input_dir' % workload.input_dir]
            t.download_output_data = ['%s.%s.gz > results/%s.%s.gz' %
                (name, workload.output, name, workload.output)]
            # t.input_staging  = [{'source': 'wf0_master.py',
            #                         'target': 'wf0_master.py',
            #                         'action': rp.TRANSFER,
            #                         'flags' : rp.DEFAULT_FLAGS},
            #                         {'source': 'wf0_worker.py',
            #                         'target': 'wf0_worker.py',
            #                         'action': rp.TRANSFER,
            #                         'flags' : rp.DEFAULT_FLAGS},
            #                         {'source': 'configs/wf0.%s.cfg' % name,
            #                         'target': 'wf0.cfg',
            #                         'action': rp.TRANSFER,
            #                         'flags' : rp.DEFAULT_FLAGS},
            #                         {'source': workload.input_dir,
            #                         'target': 'input_dir',
            #                         'action': rp.LINK,
            #                         'flags' : rp.DEFAULT_FLAGS},
            #                         {'source': workload.impress_dir,
            #                         'target': 'impress_md',
            #                         'action': rp.LINK,
            #                         'flags' : rp.DEFAULT_FLAGS},
            #                         {'source': 'read_ligand_dict.py',
            #                         'target': 'read_ligand_dict.py',
            #                         'action': rp.TRANSFER,
            #                         'flags' : rp.DEFAULT_FLAGS},
            #                     ]
            # t.output_staging = [{'source': '%s.%s.gz'         % (name, workload.output),
            #                      'target': 'results/%s.%s.gz' % (name, workload.output),
            #                      'action': rp.TRANSFER,
            #                      'flags' : rp.DEFAULT_FLAGS}]
            s.add_tasks(t)

    p.add_stages(s)

    return p

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    cfg_file  = sys.argv[1]  # resource and workload config
    run_file  = sys.argv[2]  # runs for this campaign
    session   = None

    try:

        cfg     = ru.Config(cfg=ru.read_json(cfg_file))
        runs    = check_runs(cfg_file, run_file)

        if not runs:
            print('nothing to run')
            sys.exit()

        session = rp.Session()
        pmgr    = rp.PilotManager(session=session)
        umgr    = rp.UnitManager(session=session)

        umgr.register_callback(unit_state_cb)


        # for each run in the campaign:
        #   - create pilot of requested size and runtime
        #   - create cfg with requested receptor and smiles
        #   - submit configured number of masters with that cfg on that pilot
        subs = dict()
        rurl = cfg.fs_url + cfg.workload.results
        d    = rs.filesystem.Directory(rurl)
        ls   = [str(u).split('/')[-1] for u in d.list()]

        workload  = cfg.workload

        for receptor, smiles, nodes, runtime in runs:

            print('%30s  %s'   % (receptor, smiles))
            name = '%s_-_%s'   % (receptor, smiles)
            tgt  = '%s.%s.gz'  % (name, workload.output)
            rec  = False

            if tgt in ls:
                if workload.recompute:
                    rec += 1
                    d.move(tgt, tgt + '.bak')
                else:
                    print('skip      1 %s' % name)
                    continue

            if smiles in ls:
                if smiles not in subs:
                    subs[smiles] = [str(u).split('/')[-1]  for u in d.list('%s/*' % smiles)]
                if tgt in subs[smiles]:
                    if workload.recompute:
                        rec += 2
                        d.move('%s/%s'     % (smiles, tgt),
                               '%s/%s.bak' % (smiles, tgt))
                    else:
                        print('skip      2 %s' % name)
                        continue

          # if os.path.exists('results/%s.%s.gz' % (name, wofkload.output)):
          #     print('skip      3 %s' % name)
          #     continue

            if rec: print('recompute %d %s' % (rec, name))
            else  : print('compute   2 %s'  %       name)

            cpn       = cfg.cpn
            gpn       = cfg.gpn
            n_masters = cfg.n_masters

            cfg.workload.receptor = receptor
            cfg.workload.smiles   = smiles
            cfg.workload.name     = name
            cfg.nodes             = nodes
            cfg.runtime           = runtime
            cfg.n_workers         = int(nodes / n_masters - 1)
            print('n_workers: %d'  % cfg.n_workers)

            ru.write_json(cfg, 'configs/wf0.%s.cfg' % name)

            pd = rp.ComputePilotDescription(cfg.pilot_descr)
            pd.cores   = nodes * cpn
            pd.gpus    = nodes * gpn
            pd.runtime = runtime

            pilot = pmgr.submit_pilots(pd)
            pid   = pilot.uid

            umgr.add_pilots(pilot)

            tds = list()

            for i in range(n_masters):
                td = rp.ComputeUnitDescription(cfg.master_descr)
                td.executable     = "python3"
                td.arguments      = ['wf0_master.py', i]
                td.cpu_threads    = cpn
                td.pilot          = pid
                td.input_staging  = [{'source': 'wf0_master.py',
                                      'target': 'wf0_master.py',
                                      'action': rp.TRANSFER,
                                      'flags' : rp.DEFAULT_FLAGS},
                                     {'source': 'wf0_worker.py',
                                      'target': 'wf0_worker.py',
                                      'action': rp.TRANSFER,
                                      'flags' : rp.DEFAULT_FLAGS},
                                     {'source': 'configs/wf0.%s.cfg' % name,
                                      'target': 'wf0.cfg',
                                      'action': rp.TRANSFER,
                                      'flags' : rp.DEFAULT_FLAGS},
                                     {'source': workload.input_dir,
                                      'target': 'input_dir',
                                      'action': rp.LINK,
                                      'flags' : rp.DEFAULT_FLAGS},
                                     {'source': workload.impress_dir,
                                      'target': 'impress_md',
                                      'action': rp.LINK,
                                      'flags' : rp.DEFAULT_FLAGS},
                                     {'source': 'read_ligand_dict.py',
                                      'target': 'read_ligand_dict.py',
                                      'action': rp.TRANSFER,
                                      'flags' : rp.DEFAULT_FLAGS},
                                    ]
                td.output_staging = [{'source': '%s.%s.gz'         % (name, workload.output),
                                      'target': 'results/%s.%s.gz' % (name, workload.output),
                                      'action': rp.TRANSFER,
                                      'flags' : rp.DEFAULT_FLAGS}]
                tds.append(td)

            tasks = umgr.submit_units(tds)
            p_map[pilot] = tasks

        # all pilots and masters submitted - wait for them to finish
        umgr.wait_units()

    finally:
        if session:
            session.close(download=True)


# ------------------------------------------------------------------------------

