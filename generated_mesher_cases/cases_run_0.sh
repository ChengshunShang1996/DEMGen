#!/bin/bash
#SBATCH --job-name=random_packing_part_0
#SBATCH --output=m_chengshun_job%j.out
#SBATCH --error=m_chengshun_job%j.err
#SBATCH --partition=HighParallelization
#SBATCH --ntasks-per-node=16
#SBATCH --time=10-0
cd C:\Users\cshang.PCCB201\Desktop\particle_packing_generator\generated_mesher_cases\random_case_1
python3 Kratos_Radius_expansion_method_v2.py
cd C:\Users\cshang.PCCB201\Desktop\particle_packing_generator\generated_mesher_cases\random_case_2
python3 Kratos_Radius_expansion_method_v2.py
