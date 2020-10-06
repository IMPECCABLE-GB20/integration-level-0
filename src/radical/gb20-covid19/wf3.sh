#!/bin/bash

# $1 = comp
# $2 = i
# $3 = outdir
# $4 = stage

. /sw/summit/lmod/lmod/init/profile
export WDIR="${1}" # ".format(comp),

. /sw/summit/python/3.7/anaconda3/5.3.0/etc/profile.d/conda.sh
conda activate workflow-3-4

module load cuda/9.2.148
module load gcc/7.4.0
module load spectrum-mpi/10.3.1.2-20200121

mkdir -p ${WDIR}/replicas/rep${2}/${3}  # .format(i, outdir),
cd ${WDIR}/replicas/rep${2}/${3}        # ".format(i, outdir),

rm -f ${4}.log ${4}.xml ${4}.dcd ${4}.chk # ".format(stage, stage, stage, stage),
export OMP_NUM_THREADS=1

python3 ${WDIR}/${4}.py    # '.format(stage)]