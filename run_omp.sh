#!/bin/bash
#SBATCH --job-name=DEMGen-sand
#SBATCH --output=CoFemDemForMembrane-test%j.out
#SBATCH --error=CoFemDemForMembrane-test%j.err
#SBATCH --partition=R182-open
#SBATCH --ntasks-per-node=16
##SBATCH --qos=cpu-limit32

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

python3 src/DEMGen_framework_main.py