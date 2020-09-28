import glob
from radical.entk import Pipeline, Stage, Task


def esmacs(cfg, names, stage, outdir):

    s = Stage()
    #print("DEBUG:instantiation:  %s" % len(s._tasks))

    for comp in names:
        #print("DEBUG:first loop: %s" % len(s._tasks))
        for i in range(1, 7):
            #print("DEBUG:second loop:start: %s" % len(s._tasks))
            t = Task()

            t.pre_exec = [
                "export WDIR=\"{}\"".format(comp),
                ". {}".format(cfg['conda_init']),
                "conda activate {}".format(cfg['conda_esmacs_task_env']),
                "module load {}".format(cfg['esmacs_task_modules']),
                "mkdir -p $WDIR/replicas/rep{}/{}".format(i, outdir),
                "cd $WDIR/replicas/rep{}/{}".format(i, outdir),
                "rm -f {}.log {}.xml {}.dcd {}.chk".format(stage, stage, stage, stage),
                "export OMP_NUM_THREADS=1"]

            t.executable = 'python3'
            t.arguments = ['$WDIR/{}.py'.format(stage)]
            t.post_exec = []

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
    #print("{}/input/lig*".format(cfg['run_dir']))
    #print("DEBUG:generate_esmacs:esmacs_names %s" % esmacs_names)

    p = Pipeline()
    p.name = 'ESMACS'

    s1 = esmacs(cfg, esmacs_names, stage="eq1", outdir="equilibration")
    p.add_stages(s1)

    # s2 = esmacs(cfg, esmacs_names, stage="eq2")
    # p.add_stages(s2)

    s3 = esmacs(cfg, esmacs_names, stage="sim1", outdir="simulation")
    p.add_stages(s3)

    return p
