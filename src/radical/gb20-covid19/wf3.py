import glob
from radical.entk import Pipeline, Stage, Task


def esmacs(names, stage, outdir="equilibration", name=None):

    s = Stage()

    for comp in names:
        for i in range(1, 13):
            t = Task()

            t.pre_exec = [
                "export WDIR=\"{}/{}\"".format(run_dir, name),
                ". {}".format(conda_init),
                "conda activate {}".format(esmacs_tenv),
                "module load {}".format(esmacs_tmodules),
                "mkdir -p $WDIR/replicas/rep{}/{}".format(i, outdir),
                "cd $WDIR/replicas/rep{}/{}".format(i, outdir),
                "rm -f {}.log {}.xml {}.dcd {}.chk".format(stage, stage, stage, stage),
                "export OMP_NUM_THREADS=1"]

            # t.executable = '/ccs/home/litan/miniconda3/envs/wf3/bin/python3.7'
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

    return s


def wf3(cfg):

    base_dir        = cfg['work_dir']+'/'+cfg['proj']
    run_dir         = cfg['run_dir']
    conda_init      = cfg['conda_init']
    esmacs_tenv     = cfg['conda_esmacs_task_env']
    esmacs_tmodules = cfg['esmacs_task_modules']

    esmacs_names = glob.glob("{}/input/lig*".format(run_dir))


    p = Pipeline()
    p.name = 'ESMACS'

    s1 = esmacs(esmacs_names, stage="eq1", name=comp)
    p.add_stages(s1)

    s2 = esmacs(esmacs_names, stage="eq2", name=comp)
    p.add_stages(s2)

    s3 = esmacs(esmacs_names, stage="sim1", outdir="simulation", name=comp)
    p.add_stages(s3)

    return p