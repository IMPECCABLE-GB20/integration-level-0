#Summit stack
module load python/3.7.0
module load py-virtualenv/16.0.0
module load py-setuptools/40.4.3-py3
module load zeromq
module load vim
. /ccs/home/mturilli1/gb20/integration-level-0/ve/gb20-integration-0/bin/activate

# RCT stack
export RADICAL_PILOT_DBURL="mongodb://$USERNAME:$PASSWORD@129.114.17.185:27017/rct"
export RADICAL_LOG_LVL="DEBUG"
export RADICAL_PROFILE="TRUE"
export RADICAL_ENTK_VERBOSE="TRUE"
export RMQ_HOSTNAME="129.114.17.185"
export RMQ_PORT=5672
export RMQ_USERNAME=$USERNAME
export RMQ_PASSWORD=$PASSWORD

# WF2 stack
export CONDA_OPENMM="/gpfs/alpine/proj-shared/med110/conda/openmm"
export CONDA_PYTORCH="/gpfs/alpine/proj-shared/med110/atrifan/scripts/pytorch-1.6.0_cudnn-8.0.2.39_nccl-2.7.8-1_static_mlperf"
export MOLECULES_PATH="/gpfs/alpine/proj-shared/med110/hrlee/git/braceal/molecules"
export PROJ="med110"
export WF2_BASE_PATH="$MEMBERWORK/$PROJ/DrugWorkflows/workflow-2"
