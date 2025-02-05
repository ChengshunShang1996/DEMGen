#!/bin/bash
#SBATCH --job-name=radius_expansion_main
#SBATCH --output=Mesher_case_2%j.out
#SBATCH --error=Mesher_case_2%j.err
#SBATCH --partition=B510
#SBATCH --ntasks-per-node=16

##Optional - Required memory in MB per node, or per core. Defaults are 1GB per core.
##SBATCH --mem=3096
#SBATCH --mem-per-cpu=3096
##SBATCH --exclusive

##Optional - Estimated execution time
##Acceptable time formats include  "minutes",   "minutes:seconds",
##"hours:minutes:seconds",   "days-hours",   "days-hours:minutes" ,"days-hours:minutes:seconds".
#SBATCH --time=10-0

########### Further details -> man sbatch ##########
#export OMP_NUM_THREADS=16

python3 create_particle_and_cases_for_hpc.py