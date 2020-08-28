module load python/3.7.0
module load py-virtualenv/16.0.0
module load py-setuptools/40.4.3-py3
module load zeromq
module load vim
. /ccs/home/mturilli1/gb20/integration-level-0/ve/gb20-integration-0/bin/activate
export RADICAL_PILOT_DBURL="mongodb://129.114.17.185:27017/rct"
export RADICAL_LOG_LVL="DEBUG"
export RADICAL_PROFILE="TRUE"
export RADICAL_ENTK_VERBOSE="TRUE"
export RMQ_HOSTNAME="129.114.17.185"
export RMQ_PORT=5672
export RMQ_USERNAME="mturilli"
export RMQ_PASSWORD=""
