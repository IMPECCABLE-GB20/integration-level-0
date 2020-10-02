import os, json, time
import tempfile, glob
from radical.entk import Pipeline, Stage, Task, AppManager

# Assumptions:
# - # of MD steps: 2
# - Each MD step runtime: 15 minutes
# - Summit's scheduling policy [1]
#
# Resource rquest:
# - 4 <= nodes with 2h walltime.
#
# Workflow [2]
#
# [1] https://www.olcf.ornl.gov/for-users/system-user-guides/summit/summit-user-guide/scheduling-policy
# [2] https://docs.google.com/document/d/1XFgg4rlh7Y2nckH0fkiZTxfauadZn_zSn3sh51kNyKE/
#

md_counts = 12
ml_counts = 10
node_counts = md_counts // 6


conda_path = os.environ.get('CONDA_PREFIX')
conda_openmm = os.environ.get('CONDA_OPENMM', conda_path)
conda_pytorch = os.environ.get('CONDA_PYTORCH', conda_path)
base_path = os.path.abspath('.') # '/gpfs/alpine/proj-shared/bip179/entk/hyperspace/microscope/experiments/'
molecules_path = os.environ.get('MOLECULES_PATH')
sparse_matrix_path = None

LEN_initial = 10
LEN_iter = 10

def generate_training_pipeline():
    """
    Function to generate the CVAE_MD pipeline
    """

    def generate_MD_stage(num_MD=1):
        """
        Function to generate MD stage.
        """
        s1 = Stage()
        s1.name = 'MD'
        initial_MD = True
        outlier_filepath = '%s/Outlier_search/restart_points.json' % base_path

        if os.path.exists(outlier_filepath):
            initial_MD = False
            outlier_file = open(outlier_filepath, 'r')
            outlier_list = json.load(outlier_file)
            outlier_file.close()

        # MD tasks
        time_stamp = int(time.time())
        for i in range(num_MD):
            t1 = Task()
            # https://github.com/radical-collaboration/hyperspace/blob/MD/microscope/experiments/MD_exps/fs-pep/run_openmm.py
            t1.pre_exec = ['. /sw/summit/python/3.6/anaconda3/5.3.0/etc/profile.d/conda.sh']
            t1.pre_exec += ['module load cuda/9.1.85']
            t1.pre_exec += ['conda activate %s' % conda_openmm]
            t1.pre_exec += ['export ' \
                    + 'PYTHONPATH=%s/MD_exps:%s/MD_exps/MD_utils:$PYTHONPATH' %
                    (base_path, base_path)]
            t1.pre_exec += ['cd %s/MD_exps/fs-pep' % base_path]
            t1.pre_exec += ['mkdir -p omm_runs_%d && cd omm_runs_%d' % (time_stamp+i, time_stamp+i)]
            t1.executable = ['%s/bin/python' % conda_openmm]  # run_openmm.py
            t1.arguments = ['%s/MD_exps/fs-pep/run_openmm.py' % base_path]
          #   t1.arguments += ['--topol', '%s/MD_exps/fs-pep/pdb/topol.top' % base_path]


            # pick initial point of simulation
            if initial_MD or i >= len(outlier_list):
                t1.arguments += ['--pdb_file',
                        '%s/MD_exps/fs-pep/pdb/100-fs-peptide-400K.pdb' % base_path]
            elif outlier_list[i].endswith('pdb'):
                t1.arguments += ['--pdb_file', outlier_list[i]]
                t1.pre_exec += ['cp %s ./' % outlier_list[i]]
            elif outlier_list[i].endswith('chk'):
                t1.arguments += ['--pdb_file',
                        '%s/MD_exps/fs-pep/pdb/100-fs-peptide-400K.pdb' % base_path,
                        '-c', outlier_list[i]]
                t1.pre_exec += ['cp %s ./' % outlier_list[i]]

            # how long to run the simulation
            if initial_MD:
                t1.arguments += ['--length', LEN_initial]
            else:
                t1.arguments += ['--length', LEN_iter]

            # assign hardware the task
            t1.cpu_reqs = {'processes': 1,
                           'process_type': None,
                              'threads_per_process': 4,
                              'thread_type': 'OpenMP'
                              }
            t1.gpu_reqs = {'processes': 1,
                           'process_type': None,
                              'threads_per_process': 1,
                              'thread_type': 'CUDA'
                             }

            # Add the MD task to the simulating stage
            s1.add_tasks(t1)
        return s1


    def generate_aggregating_stage():
        """
        Function to concatenate the MD trajectory (h5 contact map)
        """
        s2 = Stage()
        s2.name = 'aggregating'
        global sparse_matrix_path

        # Aggregation task
        t2 = Task()
        # https://github.com/radical-collaboration/hyperspace/blob/MD/microscope/experiments/MD_to_CVAE/MD_to_CVAE.py
        t2.pre_exec = []
        t2.pre_exec += ['. /sw/summit/python/3.6/anaconda3/5.3.0/etc/profile.d/conda.sh']
        t2.pre_exec += [f'conda activate {conda_pytorch}']
        # preprocessing for molecules' script, it needs files in a single
        # directory
        # the following pre-processing does:
        # 1) find all (.dcd) files from openmm results
        # 2) create a temp directory
        # 3) symlink them in the temp directory
        list_of_dcds = glob.glob(f'{base_path}/MD_exps/fs-pep/omm_runs*/*.dcd')
        aggregated_temp_path = tempfile.mkdtemp(dir=f'{base_path}/MD_to_CVAE',
                prefix='{}-'.format(len(list_of_dcds)))
        for i in list_of_dcds:
            new_name_from_omm_directory = os.path.basename(os.path.dirname(i))
            os.symlink(i, '{}/{}.dcd'.format(aggregated_temp_path,
                new_name_from_omm_directory))

        sparse_matrix_path = f'{aggregated_temp_path}/fs-pep.h5'
        t2.executable = [f'{conda_pytorch}/bin/python']  # MD_to_CVAE.py
        t2.arguments = [
                f'{molecules_path}/scripts/traj_to_sparse_contact_map.py',
                '-t', aggregated_temp_path,
                '-p', f'{base_path}/MD_exps/fs-pep/pdb/100-fs-peptide-400K.pdb',
                '-r', f'{base_path}/MD_exps/fs-pep/pdb/100-fs-peptide-400K.pdb',
                '-o', sparse_matrix_path,
                '-P' # parallel
                ]

        # Add the aggregation task to the aggreagating stage
        s2.add_tasks(t2)
        return s2


    def generate_ML_stage(num_ML=1):
        """
        Function to generate the learning stage
        """
        s3 = Stage()
        s3.name = 'learning'

        global sparse_matrix_path

        # learn task
        time_stamp = int(time.time())
        for i in range(num_ML):
            t3 = Task()
            # https://github.com/radical-collaboration/hyperspace/blob/MD/microscope/experiments/CVAE_exps/train_cvae.py
            t3.pre_exec = ['. /sw/summit/python/3.6/anaconda3/5.3.0/etc/profile.d/conda.sh']
            t3.pre_exec += [
                    'module load gcc/7.4.0',
                    'module load cuda/10.1.243',
                    'module load hdf5/1.10.4',
                    'export LANG=en_US.utf-8',
                    'export LC_ALL=en_US.utf-8'
                    ]
            t3.pre_exec += ['conda activate %s' % conda_pytorch]

            dim = i + 3
            cvae_dir = 'cvae_runs_%.2d_%d' % (dim, time_stamp+i)
            t3.pre_exec += [f'cd {base_path}/CVAE_exps']
            t3.pre_exec += ['mkdir -p {0} && cd {0}'.format(cvae_dir)]
            t3.executable = [f'{conda_pytorch}/bin/python']  # train_cvae.py
            t3.arguments = [
                    f'{molecules_path}/examples/example_vae.py',
                    '-i', sparse_matrix_path,
                    '-o', './',
                    '--model_id', cvae_dir,
                    # fs-pep
                    '--dim1', 22,
                    '--dim2', 22,
                    '-d', 11,
                    '-s',      # sparse matrix
                    '-b', 256, # batch size
                    '-e', 100  # epoch
                    ]

            t3.cpu_reqs = {'processes': 1,
                           'process_type': None,
                    'threads_per_process': 4,
                    'thread_type': 'OpenMP'
                    }
            t3.gpu_reqs = {'processes': 1,
                           'process_type': None,
                    'threads_per_process': 1,
                    'thread_type': 'CUDA'
                    }

            # Add the learn task to the learning stage
            s3.add_tasks(t3)
        return s3

    p = Pipeline()
    p.name = 'WF2'

    # --------------------------
    # MD stage
    s1 = generate_MD_stage(num_MD=md_counts)
    # Add simulating stage to the training pipeline
    p.add_stages(s1)

    # --------------------------
    # Aggregate stage
    s2 = generate_aggregating_stage()
    # Add the aggregating stage to the training pipeline
    p.add_stages(s2)

    # --------------------------
    # Learning stage
    s3 = generate_ML_stage(num_ML=ml_counts)
    # Add the learning stage to the pipeline
    p.add_stages(s3)

    return p


# ------------------------------------------------------------------------------
# Set default verbosity

# if os.environ.get('RADICAL_ENTK_VERBOSE') is None:
#     os.environ['RADICAL_ENTK_REPORT'] = 'True'


# if __name__ == '__main__':

#     # Create a dictionary to describe four mandatory keys:
#     # resource, walltime, cores and project
#     # resource is 'local.localhost' to execute locally
#     res_dict = {
#             'resource': 'ornl.summit',
#             'queue'   : 'batch',
#             'schema'  : 'local',
#             'walltime': 60 * 1,
#             'cpus'    : 42 * 4 * node_counts,
#             'gpus'    : 6 * node_counts,
#             'project' : 'MED110'
#     }

#     # Create Application Manager
#     appman = AppManager(hostname=os.environ.get('RMQ_HOSTNAME'),
#             port=int(os.environ.get('RMQ_PORT')),
#             username=os.environ.get('RMQ_USERNAME'),
#             password=os.environ.get('RMQ_PASSWORD'))
#     appman.resource_desc = res_dict

#     p1 = generate_training_pipeline()
#     pipelines = [p1]

#     # Assign the workflow as a list of Pipelines to the Application Manager. In
#     # this way, all the pipelines in the list will execute concurrently.
#     appman.workflow = pipelines

#     # Run the Application Manager
#     appman.run()
