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
# $10 = cfg['env_dir']
# $11 = cfg['rdbase']
# $12 = cfg['scratch_dir']

PYTHON_VER=3.6
CUDA_VER=11.0

module load gcc/7.4.0
module load python/3.6.6-anaconda3-5.3.0
module load hdf5/1.10.4
module load cuda/11.0.3

source activate ${5}

# add to path
export ENV_DIR=${10}
export CUDA_STUFF_DIR=${ENV_DIR}/cuda-${CUDA_VER//.}/targets/ppc64le-linux
export PATH=${CUDA_STUFF_DIR}/bin:${PATH}
export LD_LIBRARY_PATH=${CUDA_STUFF_DIR}/lib:${LD_LIBRARY_PATH}
# rdkit
export RDBASE=${11}
export LD_LIBRARY_PATH=${RDBASE}/lib:${LD_LIBRARY_PATH}
export PYTHONPATH=${RDBASE}:${PYTHONPATH}

export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
export device=${OMPI_COMM_WORLD_LOCAL_RANK:=0}
# export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${2}       # %s' % cfg['ld_lib_path'],
export data_root=${3}                                # %s' % cfg['data_root'],
export MPLCONFIGDIR=${12}
export FONTCONFIG_PATH=/etc/fonts

#bindcmd:
ncorespersocket=88
socket=$(( ${device} / 3 ))
bindcmd="numactl -N $(( ${socket} * 8 ))"

# openmp stuff
export OMP_PLACES=threads



cd ${4}                                              # %s' % cfg['base_path']

# unimproved run
${bindcmd} \
    /gpfs/alpine/ven201/world-shared/tkurth/attention/python_env/conda_attention_cuda-110_py-36/bin/python -u infer_images.py \
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
    -num_calibration_batches=10 \
    --distributed
