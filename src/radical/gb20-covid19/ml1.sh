#!/bin/bash

# $1 = --distributed
# $2 = cfg['ld_lib_path']
# $3 = cfg['data_root']
# $4 = cfg['base_path']
# $5 = cfg['ml1_conda_env']
# $6 = cfg['output_dir']
# $7 = cfg['model']
# $8 = cfg['trt']
# $9 = cfg['userid']


. /sw/summit/lmod/lmod/init/profile
module load gcc/7.4.0
module load python/3.6.6-anaconda3-5.3.0
module load cuda/10.1.243
module load hdf5/1.10.4

export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
export device=${OMPI_COMM_WORLD_LOCAL_RANK:=0}
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${2}       # %s' % cfg['ld_lib_path'],
export data_root=${3}                                # %s' % cfg['data_root'],

cd ${4}                                              # %s' % cfg['base_path']
source activate ${5}

# unimproved run
python3 -u infer_images.py \
    -t 0 \
    -d ${device} \
    -i "${data_root}/images_compressed/*.pkl.gz" \
    -o ${6} \
    -m ${7} \
    -trt ${8} \
    --stage_dir /mnt/bb/${9} \
    --num_stage_workers 4 \
    --output_frequency 200 \
    --update_frequency 10 \
    -b 256 \
    -j 4 \
    -dtype=fp16 \
    -num_calibration_batches=10 ${1}
