import os
import glob
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--path", help="outlier path for PDBs")
parser.add_argument("-p", "--top" , help="Workflow 2 inputs for topology files")

args = parser.parse_args()

outlier_path = os.path.abspath(args.path)
top_path     = os.path.abspath(args.top)
outlier_pdbs = sorted(glob.glob(outlier_path + '/omm_*.pdb'))

for pdb in outlier_pdbs:
    label = os.path.basename(pdb).split("_")[2]
    top_file = glob.glob(top_path + f'/input_{label}/*top')[0]
    if not os.path.exists(top_file):
        print("Error: ", top_file)
    else:
        top_name = os.path.basename(pdb)[:-4] + '.top'
        shutil.copy2(pdb, './')
        shutil.copy2(top_file, top_name)