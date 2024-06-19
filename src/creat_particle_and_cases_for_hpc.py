import os
import shutil
import random
import math

from creat_particles_inside_of_a_domain import CreatParticlesInsideOfADomain

class CreatParticlesAndCasesForHpc(CreatParticlesInsideOfADomain):

    def clear_old_mesher_cases_folder(self):
        mesher_cases_folder_name = 'generated_mesher_cases'
        
        if os.path.exists(mesher_cases_folder_name):
            shutil.rmtree(mesher_cases_folder_name, ignore_errors=True)
            os.makedirs(mesher_cases_folder_name)
        else:
            os.makedirs(mesher_cases_folder_name)

    def creat_kratos_cases(self, cases_number, nodes_num, partition_name_list):
        
        self.end_sim_file_num = 0
        self.is_sh_head_write = False
        self.sh_marker = 0
        
        for i in range(1, cases_number + 1):

            new_folder_name = 'random_case_' + str(i)
            aim_path = os.path.join(os.getcwd(),'generated_mesher_cases', new_folder_name)
            os.mkdir(aim_path)

            RVE_length_x = 0.005
            RVE_length_y = 0.005
            RVE_length_z = 0.005
            RVE_size = [RVE_length_x, RVE_length_y, RVE_length_z]
            domain_scale_multiplier = 1.0
            self.initialize(RVE_size, domain_scale_multiplier)
            self.CreatParticles()
            dem_mdpa_path = os.path.join(aim_path, 'inletPGDEM.mdpa')
            self.WriteOutGIDData(dem_mdpa_path)

            seed_file_name_list = ['Kratos_Radius_expansion_method_v2.py', 'inletPGDEM_FEM_boundary.mdpa',\
                                    'inletPGDEM_inlet.mdpa', 'ProjectParametersDEM.json', 'MaterialsDEM.json', 'run_omp.sh']
            
            for seed_file_name in seed_file_name_list:
                seed_file_path_and_name = os.path.join(os.getcwd(), 'rem_seed_files', seed_file_name)
                aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
                if seed_file_name == 'run_omp.sh':
                        with open(seed_file_path_and_name, "r") as f_run_omp:
                            with open(aim_file_path_and_name, "w") as f_run_omp_w:
                                for line in f_run_omp.readlines():
                                    if "radius_expansion_case_1_diff_a_4e5" in line:
                                        hpc_case_name = os.path.basename(aim_path)
                                        line = line.replace("radius_expansion_case_", hpc_case_name)
                                    f_run_omp_w.write(line)
                else:
                    shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)
            
            # write the cases_run.sh
            partition_name = random.choice(partition_name_list)
            self.end_sim_file_num += 1
            new_sh_marker = (self.end_sim_file_num - 1) // nodes_num
            if new_sh_marker > self.sh_marker:
                self.sh_marker = new_sh_marker
                self.is_sh_head_write = False
            sh_file_name = 'cases_run_' + str(self.sh_marker) + '.sh'

            # creat the cases_run.sh
            cases_run_path_and_name = os.path.join(os.getcwd(), 'generated_mesher_cases', sh_file_name)

            with open(cases_run_path_and_name, "a") as f_w_cases_run:
                if self.is_sh_head_write == False:
                    f_w_cases_run.write('#!/bin/bash'+'\n')
                    f_w_cases_run.write('#SBATCH --job-name=random_packing' + '_part_'+ str(self.sh_marker) +'\n')
                    f_w_cases_run.write('#SBATCH --output=m_chengshun_job%j.out'+'\n')
                    f_w_cases_run.write('#SBATCH --error=m_chengshun_job%j.err'+'\n')
                    f_w_cases_run.write('#SBATCH --partition='+ partition_name +'\n')
                    f_w_cases_run.write('#SBATCH --ntasks-per-node='+str(nodes_num)+'\n')
                    f_w_cases_run.write('#SBATCH --time=10-0' + '\n')
                    #f_w_cases_run.write('#SBATCH --nodes=1'+'\n'+'\n')
                    self.is_sh_head_write = True
                f_w_cases_run.write('cd '+ aim_path + '\n')
                f_w_cases_run.write('python3 '+ 'Kratos_Radius_expansion_method_v2.py' + '\n')
            f_w_cases_run.close()

    def run_kratos_cases(self, max_index = 1):

        for i in range(0, max_index):
            cases_run_name = 'cases_run_' + str(i) + '.sh'
            command_execution = 'sbatch generated_mesher_cases/' + cases_run_name
            os.system(command_execution)

if __name__ == "__main__":

    TestDEM = CreatParticlesAndCasesForHpc()
    TestDEM.clear_old_mesher_cases_folder()
    cases_number = 100
    nodes_num = 20
    partition_name_list = ['HighParallelization']
    TestDEM.creat_kratos_cases(cases_number, nodes_num, partition_name_list)
    max_index = 5
    TestDEM.run_kratos_cases(max_index)


    

