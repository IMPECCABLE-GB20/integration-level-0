#!/bin/bash

# $1 = comp
# $2 = i
# $3 = outdir
# $4 = stage
# $5 = cfg['conda_init']
# $6 = cfg['conda_esmacs_task_env']
# $7 = cfg['esmacs_task_modules']

. /sw/summit/lmod/lmod/init/profile
export WDIR="${1}" # ".format(comp),

. $5
conda activate $6
module load $7

mkdir -p ${WDIR}/replicas/rep${2}/${3}  # .format(i, outdir),
cd ${WDIR}/replicas/rep${2}/${3}        # ".format(i, outdir),

rm -f ${4}.log ${4}.xml ${4}.dcd ${4}.chk # ".format(stage, stage, stage, stage),
export OMP_NUM_THREADS=1

python3 ${WDIR}/${4}.py    # '.format(stage)]