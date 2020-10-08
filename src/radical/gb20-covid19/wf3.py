import glob
from radical.entk import Pipeline, Stage, Task


def esmacs(cfg, names, stage, outdir):

    s = Stage()
    s.name = 'S3.%s' % stage
    #print("DEBUG:instantiation:  %s" % len(s._tasks))

    for comp in names:
        #print("DEBUG:first loop: %s" % len(s._tasks))
        for i in range(1, cfg['n_replicas']):
            #print("DEBUG:second loop:start: %s" % len(s._tasks))
            t = Task()

            # RCT native
            t.pre_exec = [
                #". /sw/summit/lmod/lmod/init/profile",
                "export WDIR=\"{}\"".format(comp),
                ". {}".format(cfg['conda_init']),
                "conda activate {}".format(cfg['conda_esmacs_task_env']),
                "module load {}".format(cfg['esmacs_task_modules']),
                "mkdir -p $WDIR/replicas/rep{}/{}".format(i, outdir),
                "cd $WDIR/replicas/rep{}/{}".format(i, outdir),
                #"rm -f {}.log {}.xml {}.dcd {}.chk".format(stage, stage, stage, stage),
                "export OMP_NUM_THREADS=1"]

            t.executable = 'python3'
            t.arguments = ['$WDIR/{}.py'.format(stage)]

            # Bash wrapper
            #t.executable = '%s/wf3.sh' % comp
            #t.arguments  = [comp, i, outdir, stage,
            #                cfg['conda_init'],
            #                cfg['conda_esmacs_task_env'],
            #                cfg['esmacs_task_modules']]

            t.cpu_reqs = {
                'processes': 1,
                'process_type': None,
                'threads_per_process': 4,
                'thread_type': 'OpenMP'}

            t.gpu_reqs = {
                'processes': 1,
                'process_type': None,
                'threads_per_process': 1,
                'thread_type': 'CUDA'}
            s.add_tasks(t)
            #print("DEBUG:second loop:end: %s" % len(s._tasks))

    return s


def generate_esmacs(cfg):

    cfg['base_dir'] = cfg['work_dir']+'/'+cfg['proj']
    cfg['run_dir']  = cfg['base_dir']+'/'+cfg['data_dir']

    esmacs_names = glob.glob("{}/input/lig*".format(cfg['run_dir']))
    print("{}/input/lig*".format(cfg['run_dir']))
    print("DEBUG:generate_esmacs:esmacs_names %s" % esmacs_names)

    p = Pipeline()
    p.name = 'S3.ESMACS.%s' % cfg['type_esmacs'].upper()

    s1 = esmacs(cfg, esmacs_names, stage="eq1", outdir="equilibration")
    p.add_stages(s1)

    # s2 = esmacs(cfg, esmacs_names, stage="eq2", outdir="equilibration")
    # p.add_stages(s2)

    s3 = esmacs(cfg, esmacs_names, stage="sim1", outdir="simulation")
    p.add_stages(s3)

    return p
